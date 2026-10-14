import json, math, openpyxl
US = """Alabama|BHM|Birmingham|33.563|-86.754
Alaska|ANC|Anchorage|61.174|-149.996
Arizona|PHX|Phoenix|33.434|-112.012
Arkansas|LIT|Little Rock|34.729|-92.224
California|LAX|Los Angeles|33.943|-118.408
Colorado|DEN|Denver|39.862|-104.673
Connecticut|BDL|Hartford|41.939|-72.683
Delaware|ILG|Wilmington|39.679|-75.607
Florida|MCO|Orlando|28.429|-81.309
Hawaii|HNL|Honolulu|21.318|-157.922
Idaho|BOI|Boise|43.564|-116.223
Illinois|ORD|Chicago|41.978|-87.905
Indiana|IND|Indianapolis|39.717|-86.295
Iowa|DSM|Des Moines|41.534|-93.663
Kansas|ICT|Wichita|37.650|-97.433
Kentucky|SDF|Louisville|38.174|-85.736
Louisiana|MSY|New Orleans|29.993|-90.258
Maine|PWM|Portland|43.646|-70.309
Maryland|BWI|Baltimore|39.175|-76.668
Massachusetts|BOS|Boston|42.364|-71.005
Michigan|DTW|Detroit|42.212|-83.353
Minnesota|MSP|Minneapolis|44.882|-93.222
Mississippi|JAN|Jackson|32.311|-90.076
Missouri|STL|St. Louis|38.749|-90.370
Montana|BZN|Bozeman|45.778|-111.153
Nebraska|OMA|Omaha|41.303|-95.894
Nevada|LAS|Las Vegas|36.080|-115.152
New Hampshire|MHT|Manchester|42.933|-71.437
New Jersey|EWR|Newark|40.693|-74.169
New Mexico|ABQ|Albuquerque|35.040|-106.609
New York|LGA|New York|40.777|-73.873
North Carolina|CLT|Charlotte|35.214|-80.943
North Dakota|FAR|Fargo|46.921|-96.816
Ohio|CLE|Cleveland|41.412|-81.850
Oklahoma|OKC|Oklahoma City|35.393|-97.601
Oregon|PDX|Portland|45.589|-122.595
Pennsylvania|PHL|Philadelphia|39.872|-75.241
Rhode Island|PVD|Providence|41.724|-71.428
South Carolina|CHS|Charleston|32.899|-80.040
South Dakota|FSD|Sioux Falls|43.582|-96.742
Tennessee|BNA|Nashville|36.124|-86.678
Texas|DFW|Dallas-Fort Worth|32.897|-97.038
Utah|SLC|Salt Lake City|40.788|-111.978
Vermont|BTV|Burlington|44.472|-73.153
Virginia|IAD|Washington Dulles|38.953|-77.456
Washington|SEA|Seattle|47.450|-122.309
West Virginia|CRW|Charleston|38.373|-81.593
Wisconsin|MKE|Milwaukee|42.947|-87.897
Wyoming|JAC|Jackson Hole|43.607|-110.738"""
# region|country|iata|city|lat|lon|conf(H=busiest known, M=verify)
C = """North America|Canada|YYZ|Toronto|43.677|-79.631|H
North America|Mexico|MEX|Mexico City|19.436|-99.072|H
North America|Guatemala|GUA|Guatemala City|14.583|-90.527|H
North America|Belize|BZE|Belize City|17.539|-88.308|H
North America|El Salvador|SAL|San Salvador|13.441|-89.056|H
North America|Honduras|SAP|San Pedro Sula|15.453|-87.924|M
North America|Nicaragua|MGA|Managua|12.142|-86.168|H
North America|Costa Rica|SJO|San Jose|9.994|-84.209|H
North America|Panama|PTY|Panama City|9.071|-79.383|H
North America|Cuba|HAV|Havana|22.989|-82.409|H
North America|Jamaica|KIN|Kingston|17.936|-76.787|M
North America|Haiti|PAP|Port-au-Prince|18.580|-72.293|H
North America|Dominican Republic|PUJ|Punta Cana|18.567|-68.363|H
North America|Bahamas|NAS|Nassau|25.039|-77.466|H
North America|Barbados|BGI|Bridgetown|13.075|-59.492|H
North America|Trinidad and Tobago|POS|Port of Spain|10.595|-61.337|H
North America|Antigua and Barbuda|ANU|St. John's|17.137|-61.793|H
North America|Saint Lucia|UVF|Vieux Fort|13.733|-60.953|H
North America|Grenada|GND|St. George's|12.004|-61.786|H
North America|Saint Vincent and the Grenadines|SVD|Kingstown|13.144|-61.211|H
North America|Dominica|DOM|Roseau|15.547|-61.300|H
North America|Saint Kitts and Nevis|SKB|Basseterre|17.311|-62.719|H
South America|Brazil|GRU|Sao Paulo|-23.435|-46.473|H
South America|Argentina|EZE|Buenos Aires|-34.822|-58.536|H
South America|Chile|SCL|Santiago|-33.393|-70.786|H
South America|Colombia|BOG|Bogota|4.702|-74.147|H
South America|Peru|LIM|Lima|-12.022|-77.114|H
South America|Venezuela|CCS|Caracas|10.601|-66.991|M
South America|Ecuador|UIO|Quito|-0.129|-78.358|H
South America|Bolivia|VVI|Santa Cruz|-17.645|-63.135|H
South America|Paraguay|ASU|Asuncion|-25.240|-57.519|H
South America|Uruguay|MVD|Montevideo|-34.838|-56.031|H
South America|Guyana|GEO|Georgetown|6.499|-58.255|H
South America|Suriname|PBM|Paramaribo|5.453|-55.188|H
Europe|United Kingdom|LHR|London|51.470|-0.454|H
Europe|Ireland|DUB|Dublin|53.421|-6.270|H
Europe|France|CDG|Paris|49.010|2.548|H
Europe|Germany|FRA|Frankfurt|50.033|8.571|H
Europe|Spain|MAD|Madrid|40.472|-3.561|H
Europe|Italy|FCO|Rome|41.800|12.239|H
Europe|Netherlands|AMS|Amsterdam|52.309|4.764|H
Europe|Belgium|BRU|Brussels|50.901|4.484|H
Europe|Switzerland|ZRH|Zurich|47.458|8.548|H
Europe|Austria|VIE|Vienna|48.110|16.570|H
Europe|Portugal|LIS|Lisbon|38.774|-9.134|H
Europe|Greece|ATH|Athens|37.936|23.947|H
Europe|Poland|WAW|Warsaw|52.166|20.967|H
Europe|Czechia|PRG|Prague|50.101|14.260|H
Europe|Hungary|BUD|Budapest|47.439|19.262|H
Europe|Romania|OTP|Bucharest|44.572|26.102|H
Europe|Bulgaria|SOF|Sofia|42.695|23.406|H
Europe|Croatia|ZAG|Zagreb|45.743|16.069|H
Europe|Serbia|BEG|Belgrade|44.818|20.309|H
Europe|Slovakia|BTS|Bratislava|48.170|17.213|H
Europe|Slovenia|LJU|Ljubljana|46.224|14.458|H
Europe|Denmark|CPH|Copenhagen|55.618|12.656|H
Europe|Sweden|ARN|Stockholm|59.652|17.919|H
Europe|Norway|OSL|Oslo|60.194|11.100|H
Europe|Finland|HEL|Helsinki|60.317|24.963|H
Europe|Iceland|KEF|Reykjavik|63.985|-22.605|H
Europe|Estonia|TLL|Tallinn|59.413|24.833|H
Europe|Latvia|RIX|Riga|56.924|23.971|H
Europe|Lithuania|VNO|Vilnius|54.634|25.286|H
Europe|Luxembourg|LUX|Luxembourg|49.627|6.212|H
Europe|Malta|MLA|Valletta|35.857|14.477|H
Europe|Cyprus|LCA|Larnaca|34.875|33.625|H
Europe|Albania|TIA|Tirana|41.415|19.721|H
Europe|North Macedonia|SKP|Skopje|41.962|21.621|H
Europe|Bosnia and Herzegovina|SJJ|Sarajevo|43.825|18.331|H
Europe|Montenegro|TGD|Podgorica|42.359|19.252|H
Europe|Kosovo|PRN|Pristina|42.573|21.036|H
Europe|Moldova|KIV|Chisinau|46.928|28.931|H
Europe|Ukraine|KBP|Kyiv|50.345|30.895|M
Europe|Belarus|MSQ|Minsk|53.882|28.031|H
Europe|Russia|SVO|Moscow|55.973|37.415|M
Asia|India|DEL|Delhi|28.556|77.100|H
Asia|China|CAN|Guangzhou|23.392|113.299|M
Asia|Japan|HND|Tokyo|35.549|139.780|H
Asia|South Korea|ICN|Seoul|37.469|126.451|H
Asia|Taiwan|TPE|Taipei|25.078|121.233|H
Asia|Hong Kong|HKG|Hong Kong|22.308|113.915|H
Asia|Singapore|SIN|Singapore|1.364|103.991|H
Asia|Malaysia|KUL|Kuala Lumpur|2.746|101.710|H
Asia|Thailand|BKK|Bangkok|13.690|100.750|H
Asia|Vietnam|SGN|Ho Chi Minh City|10.819|106.652|H
Asia|Indonesia|CGK|Jakarta|-6.126|106.656|H
Asia|Philippines|MNL|Manila|14.509|121.020|H
Asia|Cambodia|PNH|Phnom Penh|11.547|104.844|M
Asia|Laos|VTE|Vientiane|17.988|102.563|H
Asia|Myanmar|RGN|Yangon|16.907|96.133|H
Asia|Brunei|BWN|Bandar Seri Begawan|4.944|114.928|H
Asia|Pakistan|KHI|Karachi|24.907|67.161|M
Asia|Bangladesh|DAC|Dhaka|23.843|90.398|H
Asia|Sri Lanka|CMB|Colombo|7.181|79.884|H
Asia|Nepal|KTM|Kathmandu|27.696|85.359|H
Asia|Bhutan|PBH|Paro|27.403|89.425|H
Asia|Maldives|MLE|Male|4.192|73.529|H
Asia|Afghanistan|KBL|Kabul|34.566|69.212|H
Asia|Mongolia|ULN|Ulaanbaatar|47.843|106.766|M
Asia|Kazakhstan|ALA|Almaty|43.352|77.040|M
Asia|Uzbekistan|TAS|Tashkent|41.258|69.281|H
Asia|Kyrgyzstan|FRU|Bishkek|43.061|74.478|H
Asia|Tajikistan|DYU|Dushanbe|38.543|68.825|H
Asia|Turkmenistan|ASB|Ashgabat|37.987|58.361|H
Asia|Azerbaijan|GYD|Baku|40.468|50.047|H
Asia|Armenia|EVN|Yerevan|40.147|44.396|H
Asia|Georgia|TBS|Tbilisi|41.669|44.955|H
Asia|Turkey|IST|Istanbul|41.261|28.742|H
Asia|Israel|TLV|Tel Aviv|32.011|34.887|H
Asia|Jordan|AMM|Amman|31.723|35.993|H
Asia|Lebanon|BEY|Beirut|33.821|35.488|H
Asia|Syria|DAM|Damascus|33.411|36.516|H
Asia|Iraq|BGW|Baghdad|33.262|44.235|H
Asia|Iran|IKA|Tehran|35.416|51.152|M
Asia|Kuwait|KWI|Kuwait City|29.227|47.969|H
Asia|Saudi Arabia|JED|Jeddah|21.680|39.157|M
Asia|United Arab Emirates|DXB|Dubai|25.253|55.366|H
Asia|Qatar|DOH|Doha|25.273|51.608|H
Asia|Bahrain|BAH|Manama|26.271|50.634|H
Asia|Oman|MCT|Muscat|23.593|58.284|H
Asia|Yemen|SAH|Sanaa|15.476|44.220|H
Africa|Egypt|CAI|Cairo|30.122|31.406|H
Africa|Morocco|CMN|Casablanca|33.367|-7.590|H
Africa|Algeria|ALG|Algiers|36.691|3.215|H
Africa|Tunisia|TUN|Tunis|36.851|10.227|H
Africa|Libya|TIP|Tripoli|32.664|13.159|M
Africa|Sudan|KRT|Khartoum|15.590|32.553|H
Africa|South Sudan|JUB|Juba|4.872|31.601|H
Africa|Ethiopia|ADD|Addis Ababa|8.978|38.799|H
Africa|Eritrea|ASM|Asmara|15.292|38.911|H
Africa|Djibouti|JIB|Djibouti|11.547|43.159|H
Africa|Somalia|MGQ|Mogadishu|2.014|45.305|H
Africa|Kenya|NBO|Nairobi|-1.319|36.927|H
Africa|Uganda|EBB|Entebbe|0.042|32.443|H
Africa|Tanzania|DAR|Dar es Salaam|-6.878|39.203|H
Africa|Rwanda|KGL|Kigali|-1.969|30.139|H
Africa|Burundi|BJM|Bujumbura|-3.324|29.319|H
Africa|DR Congo|FIH|Kinshasa|-4.386|15.445|H
Africa|Republic of the Congo|BZV|Brazzaville|-4.252|15.253|H
Africa|Angola|LAD|Luanda|-8.858|13.231|H
Africa|Zambia|LUN|Lusaka|-15.331|28.453|H
Africa|Zimbabwe|HRE|Harare|-17.932|31.093|H
Africa|Mozambique|MPM|Maputo|-25.921|32.573|H
Africa|Malawi|LLW|Lilongwe|-13.789|33.781|H
Africa|Madagascar|TNR|Antananarivo|-18.797|47.479|H
Africa|Mauritius|MRU|Port Louis|-20.430|57.683|H
Africa|Seychelles|SEZ|Victoria|-4.674|55.522|H
Africa|South Africa|JNB|Johannesburg|-26.139|28.246|H
Africa|Namibia|WDH|Windhoek|-22.480|17.463|H
Africa|Botswana|GBE|Gaborone|-24.557|25.918|H
Africa|Lesotho|MSU|Maseru|-29.462|27.553|H
Africa|Eswatini|SHO|Manzini|-26.358|31.717|H
Africa|Nigeria|LOS|Lagos|6.577|3.321|H
Africa|Ghana|ACC|Accra|5.605|-0.167|H
Africa|Ivory Coast|ABJ|Abidjan|5.261|-3.926|H
Africa|Senegal|DSS|Dakar|14.670|-17.073|H
Africa|Mali|BKO|Bamako|12.534|-7.950|H
Africa|Burkina Faso|OUA|Ouagadougou|12.353|-1.512|H
Africa|Niger|NIM|Niamey|13.481|2.183|H
Africa|Chad|NDJ|N'Djamena|12.134|15.034|H
Africa|Cameroon|DLA|Douala|4.006|9.719|H
Africa|Gabon|LBV|Libreville|0.459|9.412|H
Africa|Equatorial Guinea|SSG|Malabo|3.755|8.709|H
Africa|Central African Republic|BGF|Bangui|4.399|18.519|H
Africa|Benin|COO|Cotonou|6.357|2.384|H
Africa|Togo|LFW|Lome|6.166|1.254|H
Africa|Guinea|CKY|Conakry|9.576|-13.612|H
Africa|Sierra Leone|FNA|Freetown|8.616|-13.196|H
Africa|Liberia|ROB|Monrovia|6.234|-10.362|H
Africa|Gambia|BJL|Banjul|13.338|-16.652|H
Africa|Guinea-Bissau|OXB|Bissau|11.895|-15.654|H
Africa|Mauritania|NKC|Nouakchott|18.098|-15.948|H
Africa|Cape Verde|RAI|Praia|14.945|-23.494|H
Africa|Comoros|HAH|Moroni|-11.533|43.272|H
Africa|Sao Tome and Principe|TMS|Sao Tome|0.378|6.712|H
Oceania|Australia|SYD|Sydney|-33.946|151.177|H
Oceania|New Zealand|AKL|Auckland|-37.008|174.792|H
Oceania|Fiji|NAN|Nadi|-17.755|177.443|H
Oceania|Papua New Guinea|POM|Port Moresby|-9.443|147.220|H
Oceania|Samoa|APW|Apia|-13.830|-172.008|H
Oceania|Tonga|TBU|Nuku'alofa|-21.241|-175.150|H
Oceania|Vanuatu|VLI|Port Vila|-17.699|168.320|H
Oceania|Solomon Islands|HIR|Honiara|-9.428|160.055|H
Oceania|Palau|ROR|Koror|7.367|134.544|H"""
# extra origin-only airports
X = """BLR|Bengaluru|India|Asia|13.199|77.706
BOM|Mumbai|India|Asia|19.089|72.868
MAA|Chennai|India|Asia|12.994|80.169
HYD|Hyderabad|India|Asia|17.240|78.429
CCU|Kolkata|India|Asia|22.655|88.447
ATL|Atlanta|United States|North America|33.637|-84.428
JFK|New York|United States|North America|40.640|-73.779
SFO|San Francisco|United States|North America|37.619|-122.375
MIA|Miami|United States|North America|25.795|-80.287
LHR_dup|x|x|x|0|0"""

E = """VTZ|Visakhapatnam|India|Asia|17.721|83.225
HGI|Itanagar|India|Asia|27.095|93.653
GAU|Guwahati|India|Asia|26.106|91.586
PAT|Patna|India|Asia|25.591|85.088
RPR|Raipur|India|Asia|21.181|81.739
GOI|Goa|India|Asia|15.380|73.831
AMD|Ahmedabad|India|Asia|23.077|72.634
KUU|Kullu|India|Asia|31.877|77.154
IXR|Ranchi|India|Asia|23.314|85.322
COK|Kochi|India|Asia|10.152|76.402
IDR|Indore|India|Asia|22.722|75.801
IMF|Imphal|India|Asia|24.760|93.897
SHL|Shillong|India|Asia|25.704|91.979
AJL|Aizawl|India|Asia|23.841|92.620
DMU|Dimapur|India|Asia|25.883|93.772
BBI|Bhubaneswar|India|Asia|20.244|85.818
ATQ|Amritsar|India|Asia|31.709|74.797
JAI|Jaipur|India|Asia|26.824|75.812
PYG|Gangtok|India|Asia|27.226|88.586
IXA|Agartala|India|Asia|23.887|91.241
LKO|Lucknow|India|Asia|26.761|80.889
DED|Dehradun|India|Asia|30.190|78.180
IXC|Chandigarh|India|Asia|30.673|76.789
SXR|Srinagar|India|Asia|33.987|74.774
IXL|Leh|India|Asia|34.136|77.546
PNY|Puducherry|India|Asia|11.968|79.810
IXZ|Port Blair|India|Asia|11.641|92.730
AGX|Agatti|India|Asia|10.824|72.176
YUL|Montreal|Canada|North America|45.470|-73.741
YVR|Vancouver|Canada|North America|49.195|-123.184
YYC|Calgary|Canada|North America|51.114|-114.020
YWG|Winnipeg|Canada|North America|49.910|-97.239
YXE|Saskatoon|Canada|North America|52.171|-106.700
YHZ|Halifax|Canada|North America|44.881|-63.509
YQM|Moncton|Canada|North America|46.112|-64.679
YYT|St. John's|Canada|North America|47.619|-52.752
YYG|Charlottetown|Canada|North America|46.290|-63.121
YXY|Whitehorse|Canada|North America|60.710|-135.067
YZF|Yellowknife|Canada|North America|62.463|-114.440
YFB|Iqaluit|Canada|North America|63.756|-68.556
MEL|Melbourne|Australia|Oceania|-37.673|144.843
BNE|Brisbane|Australia|Oceania|-27.384|153.117
PER|Perth|Australia|Oceania|-31.940|115.967
ADL|Adelaide|Australia|Oceania|-34.945|138.531
HBA|Hobart|Australia|Oceania|-42.836|147.511
CBR|Canberra|Australia|Oceania|-35.307|149.195
DRW|Darwin|Australia|Oceania|-12.415|130.877
MUC|Munich|Germany|Europe|48.354|11.786
STR|Stuttgart|Germany|Europe|48.690|9.222
BER|Berlin|Germany|Europe|52.367|13.504
BRE|Bremen|Germany|Europe|53.047|8.787
HAM|Hamburg|Germany|Europe|53.630|9.988
HAJ|Hanover|Germany|Europe|52.461|9.685
DUS|Dusseldorf|Germany|Europe|51.289|6.767
HHN|Hahn|Germany|Europe|49.949|7.264
SCN|Saarbrucken|Germany|Europe|49.215|7.110
LEJ|Leipzig|Germany|Europe|51.424|12.236
ERF|Erfurt|Germany|Europe|50.980|10.958
RLG|Rostock|Germany|Europe|53.918|12.278"""
DIV = {
 "India": "Andhra Pradesh:VTZ,Arunachal Pradesh:HGI,Assam:GAU,Bihar:PAT,Chhattisgarh:RPR,Goa:GOI,Gujarat:AMD,Himachal Pradesh:KUU,Jharkhand:IXR,Karnataka:BLR,Kerala:COK,Madhya Pradesh:IDR,Maharashtra:BOM,Manipur:IMF,Meghalaya:SHL,Mizoram:AJL,Nagaland:DMU,Odisha:BBI,Punjab:ATQ,Rajasthan:JAI,Sikkim:PYG,Tamil Nadu:MAA,Telangana:HYD,Tripura:IXA,Uttar Pradesh:LKO,Uttarakhand:DED,West Bengal:CCU,Delhi:DEL,Chandigarh:IXC,Jammu and Kashmir:SXR,Ladakh:IXL,Puducherry:PNY,Andaman and Nicobar Islands:IXZ,Lakshadweep:AGX",
 "Canada": "Ontario:YYZ,Quebec:YUL,British Columbia:YVR,Alberta:YYC,Manitoba:YWG,Saskatchewan:YXE,Nova Scotia:YHZ,New Brunswick:YQM,Newfoundland and Labrador:YYT,Prince Edward Island:YYG,Yukon:YXY,Northwest Territories:YZF,Nunavut:YFB",
 "Australia": "New South Wales:SYD,Victoria:MEL,Queensland:BNE,Western Australia:PER,South Australia:ADL,Tasmania:HBA,Australian Capital Territory:CBR,Northern Territory:DRW",
 "Germany": "Baden-Wurttemberg:STR,Bavaria:MUC,Berlin:BER,Bremen:BRE,Hamburg:HAM,Hesse:FRA,Mecklenburg-Vorpommern:RLG,Lower Saxony:HAJ,North Rhine-Westphalia:DUS,Rhineland-Palatinate:HHN,Saarland:SCN,Saxony:LEJ,Thuringia:ERF",
}
def hav(a,b,c,d):
    R=3958.8; p=math.pi/180
    x=math.sin((c-a)*p/2)**2+math.cos(a*p)*math.cos(c*p)*math.sin((d-b)*p/2)**2
    return 2*R*math.asin(math.sqrt(x))
ATL=(33.637,-84.428)
ws=openpyxl.load_workbook('/mnt/user-data/uploads/ATL.xlsx',data_only=True).active
ref={r[1]:float(str(r[4]).split()[0]) for r in list(ws.iter_rows(values_only=True))[1:] if r[0]}
ref['FSD']=ref.get('FDS')
A=[]; bad=[]
for l in US.split('\n'):
    st,i,city,la,lo=l.split('|'); la=float(la); lo=float(lo)
    A.append(dict(iata=i,city=city,country='United States',region='North America',sub=st,lat=la,lon=lo,primary=False,usState=True,conf='H'))
    h=hav(*ATL,la,lo); r=ref.get(i)
    if r and abs(h-r)/r>0.05 and i!='ATL': bad.append((i,round(h),r))
for l in C.split('\n'):
    rg,co,i,city,la,lo,cf=l.split('|')
    A.append(dict(iata=i,city=city,country=co,region=rg,sub='',lat=float(la),lon=float(lo),primary=True,usState=False,conf=cf))
for l in X.split('\n')[:-1]:
    i,city,co,rg,la,lo=l.split('|')
    A.append(dict(iata=i,city=city,country=co,region=rg,sub='',lat=float(la),lon=float(lo),primary=(i=='ATL'),usState=False,conf='H'))
for l in E.split('\n'):
    i,city,co,rg,la,lo=l.split('|')
    A.append(dict(iata=i,city=city,country=co,region=rg,sub='',lat=float(la),lon=float(lo),primary=False,usState=False,conf='H'))
DIVS={'United States':[[l.split('|')[0],l.split('|')[1]] for l in US.split('\n')]}
for co,v in DIV.items():
    DIVS[co]=[[x.rsplit(':',1)[0],x.rsplit(':',1)[1]] for x in v.split(',')]
codes=[a['iata'] for a in A]
dup={c for c in codes if codes.count(c)>1}
print('airports',len(A),'countries',sum(a['primary'] for a in A),'US states',sum(a['usState'] for a in A),'dups',dup)
print('US distance mismatches >5% vs your sheet:',bad)
open('airports.js','w').write('// Airport table. primary=true marks the single most-used airport chosen for each country; conf=M means verify.\nwindow.ADMI_AIRPORTS = '+json.dumps(A,separators=(',',':'))+';\nwindow.ADMI_DIVISIONS = '+json.dumps(DIVS,separators=(',',':'))+';\n')

byc={a['iata']:a for a in A}
miss=[(co,n,c) for co,l in DIVS.items() for n,c in l if c not in byc]
print('division codes missing from airport table:',miss)
for co,l in DIVS.items(): print(co,len(l))
def d(a,b): x,y=byc[a],byc[b]; return round(hav(x['lat'],x['lon'],y['lat'],y['lon']))
print('sanity (miles): BLR-DEL',d('BLR','DEL'),'(~1080) BLR-BOM',d('BLR','BOM'),'(~523) BLR-MAA',d('BLR','MAA'),'(~180) BLR-CCU',d('BLR','CCU'),'(~1000) YYZ-YVR',d('YYZ','YVR'),'(~2090) SYD-PER',d('SYD','PER'),'(~2040) MUC-HAM',d('MUC','HAM'),'(~380) BLR-IXZ',d('BLR','IXZ'),'(~1,000-1,150)')
