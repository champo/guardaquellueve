import datetime
import re
import urllib
import logging

# guardaquellueve

# This is the "grab weather information" script

def get_station_and_gmt(querystr):
	doc = urllib.urlopen("http://www.wunderground.com/cgi-bin/findweather/getForecast?wuSelect=WEATHER&query="+urllib.quote(querystr)).read()
	findings = re.search('/cgi-bin/findweather/getForecast\?query=zmw:([0-9.]+)&hourly=1&yday=([0-9]{1,3})', doc)
	if not findings:
		return None
	else:
		gmt = re.search('\(GMT ([+-][0-9]{2})\)', doc).groups()[0]
		name = re.search('<h1>([^<]+)</h1>', doc).groups()[0]
		retval = {'station': findings.groups()[0], 'gmt': int(gmt), 'name': name}
		return retval

def get_forecast_for_day(station, day):
	doc = urllib.urlopen("http://www.wunderground.com/cgi-bin/findweather/getForecast?hourly=1&query=zmw:"+station+"&yday="+day).read()
	doc = doc[:doc.find("Forecast Summary")]
	hours = []
	retvals = []
	engine = re.compile('[0-9]{1,2}&nbsp;[AP]M')
	findings = engine.search(doc)
	while findings:
		newh = findings.group().replace("&nbsp;", " ")
		if newh[:2] == "12":
			newh = "00"+newh[2:]
		hours.append(newh)
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

RAINY_STRINGS = ['chancerain', 'rain', 'tstorms', 'chancetstorms']

def _get_utc(delta, time, timezone):
	day = datetime.datetime.fromordinal((datetime.datetime.utcnow().toordinal()+delta))
	day += datetime.timedelta(0, 3600*(int(time.split(' ')[0])+12*int(time.split(' ')[1] == "PM")))
	day += datetime.timedelta(0, 3600*int(timezone))
	return day

def get_next_rainy_day(station, timezone):
	# returns None if there is no rainy day in the next 5 days
	# returns "Day, Time, Forecast" if there is a rainy day
	today = int(datetime.datetime.now().strftime("%j"))
	for delta in range(5):
		forecasts = get_forecast_for_day(station, str(today+delta))
		for forecast in forecasts:
			utc_time = _get_utc(delta, forecast[0], timezone)
			if utc_time > datetime.datetime.utcnow() and forecast[1] in RAINY_STRINGS:
				return (utc_time, forecast[1])
	return None
