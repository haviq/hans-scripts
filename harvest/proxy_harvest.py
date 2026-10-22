#!/usr/bin/env python3
# proxy_harvest.py - harvest proxy publik sedunia, validasi hidup + geo.
import concurrent.futures as cf
import ipaddress, json, os, re, time
import requests

OUT = os.environ.get("OUT", "/tmp/proxyfarm")
os.makedirs(OUT, exist_ok=True)
TIMEOUT = 6
WORKERS = 150

SOURCES = {
 "http": [
  "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
  "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
  "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
  "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
  "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
  "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
  "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
 ],
 "socks4": [
  "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
  "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
 ],
 "socks5": [
  "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
  "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
  "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
 ],
}

IPRE = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){3}):(\d{2,5})$")
ALIVE = "http://cp.cloudflare.com/generate_204"


def fetch(url):
    got = set()
    try:
        r = requests.get(url, timeout=20)
        for line in r.text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = IPRE.match(line)
            if m:
                got.add(f"{m.group(1)}:{m.group(2)}")
    except Exception:
        pass
    return got


def valid_ip(host):
    try:
        ipaddress.ip_address(host); return True
    except Exception:
        return False


def alive(proto, addr):
    scheme = proto
    px = f"{scheme}://{addr}"
    proxies = {"http": px, "https": px}
    t0 = time.time()
    try:
        r = requests.get(ALIVE, proxies=proxies, timeout=TIMEOUT)
        if r.status_code in (200, 204):
            return {"proto": proto, "addr": addr, "latency_ms": int((time.time() - t0) * 1000)}
    except Exception:
        return None
    return None


def geo(addr, proto):
    scheme = proto
    px = f"{scheme}://{addr}"
    try:
        r = requests.get("http://ip-api.com/json/?fields=status,country,countryCode,city,isp,query",
                         proxies={"http": px, "https": px}, timeout=8)
        d = r.json()
        if d.get("status") == "success":
            return d
    except Exception:
        pass
    return {}


def main():
    print(f"[*] harvest ...", flush=True)
    pool = {}
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(fetch, u): k for k, urls in SOURCES.items() for u in urls}
        for f in cf.as_completed(futs):
            k = futs[f]
            pool.setdefault(k, set()).update(f.result())
    total = sum(len(v) for v in pool.values())
    for k, v in pool.items():
        print(f"  {k}: {len(v)} raw", flush=True)
    print(f"[*] total raw: {total}", flush=True)

    jobs = []
    for proto, addrs in pool.items():
        for a in addrs:
            if valid_ip(a.split(":")[0]):
                jobs.append((proto, a))
    jobs = list(dict.fromkeys(jobs))
    print(f"[*] alive-check {len(jobs)} (workers={WORKERS}, timeout={TIMEOUT}s) ...", flush=True)

    live = []
    done = 0
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(alive, p, a) for p, a in jobs]
        for f in cf.as_completed(futs):
            done += 1
            r = f.result()
            if r:
                live.append(r)
            if done % 1000 == 0:
                print(f"  {done}/{len(jobs)} checked, {len(live)} alive", flush=True)

    live.sort(key=lambda x: x["latency_ms"])
    print(f"[+] ALIVE: {len(live)}", flush=True)

    print("[*] geo-locate (throttled 40/min) ...", flush=True)
    out = []
    for i, x in enumerate(live):
        g = geo(x["addr"], x["proto"])
        out.append({
            "proxy": f"{x['proto']}://{x['addr']}",
            "latency_ms": x["latency_ms"],
            "ip": g.get("query", x["addr"].split(":")[0]),
            "country": g.get("country"), "cc": g.get("countryCode"),
            "city": g.get("city"), "isp": g.get("isp"),
        })
        if (i + 1) % 40 == 0:
            print(f"  geo {i+1}/{len(live)}", flush=True)
            time.sleep(60)
        else:
            time.sleep(1.5)

    with open(f"{OUT}/live.json", "w") as fh:
        json.dump(out, fh, indent=1)
    for proto in ("http", "socks4", "socks5"):
        rows = [x for x in out if x["proxy"].startswith(proto)]
        with open(f"{OUT}/{proto}.txt", "w") as fh:
            for x in rows:
                fh.write(x["proxy"].replace(f"{proto}://", "") + "\n")
    with open(f"{OUT}/all.txt", "w") as fh:
        for x in out:
            fh.write(x["proxy"] + "\n")
    byc = {}
    for x in out:
        byc[x["cc"]] = byc.get(x["cc"], 0) + 1
    print(f"[+] LIVE: {len(out)} total", flush=True)
    print("[+] by country:", json.dumps(dict(sorted(byc.items(), key=lambda kv: -kv[1])[:25])), flush=True)
    print(f"[+] saved: {OUT}/live.json all.txt http.txt socks4.txt socks5.txt", flush=True)


if __name__ == "__main__":
    main()
