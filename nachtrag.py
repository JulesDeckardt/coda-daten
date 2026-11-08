# Nachtrag für Coda (Nr. 340): frei zugängliche Quellen, keine Schlüssel.
# neu   – Buchpreise der letzten 13 Monate (Gewinner und Shortlists), Bestenlisten
# alles – zusätzlich alle Buchpreise seit 1950
import json, sys, time, re, urllib.request, urllib.parse, datetime
MODE = sys.argv[1] if len(sys.argv) > 1 else 'neu'
UA = 'Coda/2.3 (private Android-App; Nachtrag)'
def get(url, accept='application/json', raw=False, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': accept}), timeout=60) as r:
                b = r.read(); return b.decode('utf-8', 'replace') if raw else json.loads(b)
        except Exception as e:
            print('Fehler', str(e)[:200]); time.sleep(75 if '429' in str(e) else 10 * (i + 1))
    return None
AWARDS = ['Booker Prize', 'Pulitzer Prize for Fiction', 'National Book Award for Fiction', 'German Book Prize', 'Leipzig Book Fair Prize', 'International Booker Prize',
    "Women's Prize for Fiction", 'Prix Goncourt', 'Wilhelm Raabe Literature Prize', 'Bavarian Book Prize', 'Pulitzer Prize for General Nonfiction', 'National Book Award for Nonfiction',
    'Deutscher Sachbuchpreis', 'Baillie Gifford Prize', 'Pulitzer Prize for History', 'Pulitzer Prize for Biography', 'Pulitzer Prize for Memoir or Autobiography',
    'Hugo Award for Best Novel', 'Nebula Award for Best Novel', 'Locus Award for Best Science Fiction Novel', 'Locus Award for Best Fantasy Novel', 'Arthur C. Clarke Award',
    'Bram Stoker Award for Best Novel', 'Kurd-Laßwitz-Preis', 'World Fantasy Award—Novel', 'Edgar Award for Best Novel', 'Gold Dagger', 'Deutscher Krimi Preis',
    'Friedrich-Glauser-Preis', 'Ian Fleming Steel Dagger', 'Thriller Award', 'Shirley Jackson Award', 'Swiss Book Prize', 'Prix Femina']
def buchpreise(since):
  out = []
  for i in range(0, len(AWARDS), 6):
    out += buchpreise1(since, AWARDS[i:i + 6]); time.sleep(65)   # Wikidata erlaubt zeitweise nur eine Abfrage pro Minute
  return out
def buchpreise1(since, aw):
    names = ' '.join('"%s"@en' % n.replace('"', '\\"') for n in aw)
    q = f"""SELECT ?work ?workLabel ?authorLabel ?awardEn ?date ?kind WHERE {{
      VALUES ?awardEn {{ {names} }} ?award rdfs:label ?awardEn .
      {{ ?x p:P166 ?s . ?s ps:P166 ?award . BIND("win" AS ?kind) }} UNION {{ ?x p:P1411 ?s . ?s ps:P1411 ?award . BIND("nom" AS ?kind) }}
      ?s pq:P585 ?date . FILTER(YEAR(?date) >= {since})
      OPTIONAL {{ ?s pq:P1686 ?fw }} BIND(COALESCE(?fw, ?x) AS ?work) FILTER NOT EXISTS {{ ?work wdt:P31 wd:Q5 }}
      OPTIONAL {{ ?work wdt:P50 ?author }} SERVICE wikibase:label {{ bd:serviceParam wikibase:language "de,en". }} }}"""
    j = get('https://query.wikidata.org/sparql?' + urllib.parse.urlencode({'query': q, 'format': 'json'}), 'application/sparql-results+json') or {}
    print('Abfrage', aw[0], len((j.get('results') or {}).get('bindings') or []))
    out = []
    for r in (j.get('results') or {}).get('bindings') or []:
        t = r.get('workLabel', {}).get('value', ''); a = r.get('authorLabel', {}).get('value', '')
        if not t or re.match(r'^Q\d+$', t): continue
        if re.match(r'^Q\d+$', a): a = ''
        d = r['date']['value'][:10]
        out.append([t, a, r['awardEn']['value'], r['kind']['value'], int(d[:4]), d])
    return out
today = datetime.date.today()
res = {'stand': today.isoformat(), 'modus': MODE}
res['buchpreise'] = buchpreise(1950 if MODE == 'alles' else today.year - 1)
try:
    old = json.load(open('nachtrag.json'))
    for k in ('buchlisten',):
        if k in old: res[k] = old[k]
    if not res['buchpreise'] and old.get('buchpreise'): res['buchpreise'] = old['buchpreise']   # Abfrage gescheitert: alten Stand behalten
except Exception:
    pass
json.dump(res, open('nachtrag.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('Buchpreise', len(res['buchpreise']))
