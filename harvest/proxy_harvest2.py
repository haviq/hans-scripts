#!/usr/bin/env python3
# proxy_harvest2.py - fast harvest + alive + geo (concurrent, no throttle)
import concurrent.futures as cf
import ipaddress, json, os, re, time
import requests

OUT = os.environ.get("OUT", "/tmp/proxyfarm")
os.makedirs(OUT, exist_ok=True)
TIMEOUT = 6
WORKERS = 300

SOURCES = [
 "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
 "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
 "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
 "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
 "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
 "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
 "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
 "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
 "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
 "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
 "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
 "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
]
IPRE = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){3}):(\d{2,5})$")
GEO = "http://ip-api.com/json/?fields=status,country,countryCode,city,isp,query"


def fetch(url):
    got = set()
    try:
        for line in requests.get(url, timeout=20).text.splitlines():
            m = IPRE.match(line.strip())
            if m:
                got.add(f"{m.group(1)}:{m.group(2)}")
    except Exception:
        pass
    return got


def valid(h):
    try:
        ipaddress.ip_address(h); return True
    except Exception:
        return False


def probe(addr):
    for proto in ("http", "socks5", "socks4"):
        px = f"{proto}://{addr}"
        t0 = time.time()
        try:
            d = requests.get(GEO, proxies={"http": px, "https": px}, timeout=TIMEOUT).json()
            if d.get("status") == "success":
                return {"proxy": f"{proto}://{addr}", "latency_ms": int((time.time()-t0)*1000),
                        "ip": d.get("query"), "country": d.get("country"), "cc": d.get("countryCode"),
                        "city": d.get("city"), "isp": d.get("isp")}
        except Exception:
            continue
    return None


def main():
    print("[*] harvest ...", flush=True)
    pool = set()
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        for r in ex.map(fetch, SOURCES):
            pool |= r
    print(f"[*] raw: {len(pool)}", flush=True)
    jobs = [a for a in pool if valid(a.split(":")[0])]
    jobs = list(dict.fromkeys(jobs))
    print(f"[*] probing {len(jobs)} (workers={WORKERS}, t={TIMEOUT}s) ...", flush=True)
    live, done = [], 0
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for r in ex.map(probe, jobs):
            done += 1
            if r:
                live.append(r)
            if done % 2000 == 0:
                print(f"  {done}/{len(jobs)} checked, {len(live)} alive", flush=True)
    live.sort(key=lambda x: x["latency_ms"])
    json.dump(live, open(f"{OUT}/live.json", "w"), indent=1)
    for proto in ("http", "socks4", "socks5"):
        with open(f"{OUT}/{proto}.txt", "w") as fh:
            for x in live:
                if x["proxy"].startswith(proto):
                    fh.write(x["proxy"].replace(f"{proto}://", "") + "\n")
    with open(f"{OUT}/all.txt", "w") as fh:
        for x in live:
            fh.write(x["proxy"] + "\n")
    byc = {}
    for x in live:
        byc[x["cc"]] = byc.get(x["cc"], 0) + 1
    print(f"[+] LIVE: {len(live)}", flush=True)
    print("[+] by country:", json.dumps(dict(sorted(byc.items(), key=lambda kv: -kv[1])[:25])), flush=True)
    print(f"[+] saved {OUT}", flush=True)


if __name__ == "__main__":
    main()
