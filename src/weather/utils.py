import re
import urllib

# guardaquellueve

# This is the "grab weather information" script

def get_station_and_days(querystr):
    engine = re.compile('/cgi-bin/findweather/getForecast\?query=zmw:([0-9.]+)&hourly=1&yday=([0-9]{1,3})')
    doc = urllib.urlopen("http://www.wunderground.com/cgi-bin/findweather/getForecast?wuSelect=WEATHER&query="+urllib.quote(querystr)).read()
    findings = engine.search(doc)
    if not findings:
        return None
    else:
        retval = {'station': findings.groups()[0], 'days': []}
        while findings:
            retval['days'].append(findings.groups()[1])
            doc = doc[findings.end():]
            findings = engine.search(doc)
        return retval

def get_forecast_for_day(station, day):
    doc = urllib.urlopen("http://www.wunderground.com/cgi-bin/findweather/getForecast?hourly=1&query=zmw:"+station+"&yday="+day).read()
    doc = doc[:doc.find("Forecast Summary")]
    hours = []
    retvals = []
    engine = re.compile('[0-9]{1,2}&nbsp;[AP]M')
    findings = engine.search(doc)
    while findings:
        hours.append(findings.group().replace("&nbsp;", " "))
        doc = doc[findings.end():]
        findings = engine.search(doc)
    engine = re.compile('http://icons-pe.wxug.com/i/c/a/(nt_)?([a-z]+)\.gif')
    findings = engine.search(doc)
    while findings:
        retvals.append(findings.groups()[1])
        doc = doc[findings.end():]
        findings = engine.search(doc)
    try:
        return [(hours[i], retvals[i]) for i in range(len(retvals))]
    except:
        return [(0, r) for r in retvals]