from .schemas import City, CityInfo, Coordinates, DriverProfile, Neighborhood


def _hood(code: str, label: str, lat: float, lng: float) -> Neighborhood:
    return Neighborhood(code=code, label=label, coordinates=Coordinates(lat=lat, lng=lng))


CITIES: dict[City, CityInfo] = {
    City.douala: CityInfo(
        code=City.douala, label="Douala", country="Cameroon",
        center=Coordinates(lat=4.0511, lng=9.7679), operator_partner="MTN Cameroon",
        neighborhoods=[
            _hood("akwa", "Akwa", 4.0470, 9.7039),
            _hood("bonanjo", "Bonanjo", 4.0490, 9.6920),
            _hood("bonapriso", "Bonapriso", 4.0381, 9.7019),
            _hood("bonaberi", "Bonabéri", 4.0823, 9.6792),
            _hood("makepe", "Makepé", 4.0718, 9.7540),
            _hood("bepanda", "Bepanda", 4.0689, 9.7304),
            _hood("ndokoti", "Ndokoti", 4.0420, 9.7505),
            _hood("logbaba", "Logbaba", 4.0631, 9.7710),
            _hood("deido", "Deido", 4.0633, 9.7000),
            _hood("aeroport", "Aéroport de Douala", 4.0061, 9.7195),
        ],
    ),
    City.yaounde: CityInfo(
        code=City.yaounde, label="Yaoundé", country="Cameroon",
        center=Coordinates(lat=3.8480, lng=11.5021), operator_partner="Orange Cameroun",
        neighborhoods=[
            _hood("centre", "Centre-ville", 3.8667, 11.5167),
            _hood("bastos", "Bastos", 3.8920, 11.5070),
            _hood("mvog-mbi", "Mvog-Mbi", 3.8569, 11.5161),
            _hood("essos", "Essos", 3.8775, 11.5333),
            _hood("nsam", "Nsam", 3.8369, 11.5180),
            _hood("mendong", "Mendong", 3.8284, 11.4748),
            _hood("nsimeyong", "Nsimeyong", 3.8278, 11.4958),
            _hood("aeroport", "Aéroport de Nsimalen", 3.7222, 11.5532),
        ],
    ),
    City.lagos: CityInfo(
        code=City.lagos, label="Lagos", country="Nigeria",
        center=Coordinates(lat=6.5244, lng=3.3792), operator_partner="MTN Nigeria",
        neighborhoods=[
            _hood("victoria-island", "Victoria Island", 6.4281, 3.4216),
            _hood("ikoyi", "Ikoyi", 6.4495, 3.4340),
            _hood("lekki", "Lekki", 6.4698, 3.5852),
            _hood("ikeja", "Ikeja", 6.6018, 3.3515),
            _hood("yaba", "Yaba", 6.5078, 3.3789),
            _hood("surulere", "Surulere", 6.4977, 3.3565),
            _hood("airport", "Murtala Muhammed Airport", 6.5774, 3.3211),
        ],
    ),
    City.nairobi: CityInfo(
        code=City.nairobi, label="Nairobi", country="Kenya",
        center=Coordinates(lat=-1.2921, lng=36.8219), operator_partner="Safaricom",
        neighborhoods=[
            _hood("cbd", "Central Business District", -1.2864, 36.8172),
            _hood("westlands", "Westlands", -1.2667, 36.8019),
            _hood("karen", "Karen", -1.3194, 36.7081),
            _hood("kilimani", "Kilimani", -1.2891, 36.7846),
            _hood("eastleigh", "Eastleigh", -1.2717, 36.8508),
            _hood("kasarani", "Kasarani", -1.2236, 36.8983),
            _hood("airport", "JKIA Airport", -1.3192, 36.9278),
        ],
    ),
    City.dakar: CityInfo(
        code=City.dakar, label="Dakar", country="Senegal",
        center=Coordinates(lat=14.7167, lng=-17.4677), operator_partner="Orange Sénégal",
        neighborhoods=[
            _hood("plateau", "Plateau", 14.6708, -17.4364),
            _hood("medina", "Médina", 14.6831, -17.4500),
            _hood("almadies", "Almadies", 14.7444, -17.5158),
            _hood("ouakam", "Ouakam", 14.7236, -17.4894),
            _hood("yoff", "Yoff", 14.7572, -17.4836),
            _hood("parcelles", "Parcelles Assainies", 14.7711, -17.4256),
            _hood("airport", "Aéroport AIBD", 14.6700, -17.0733),
        ],
    ),
}


def _drv(idx, name, phone, carrier, city, lat, lng, dlat, dlng, vehicle, plate, rating, rides,
         color, device, num_ok, sim_swap, qod, congestion, geofence=True) -> DriverProfile:
    return DriverProfile(
        id=f"drv-{idx}",
        name=name,
        phone_number=phone,
        carrier=carrier,
        city=city,
        vehicle=vehicle,
        plate=plate,
        rating=rating,
        rides_completed=rides,
        avatar_color=color,
        current_location=Coordinates(lat=lat, lng=lng),
        network_location=Coordinates(lat=dlat, lng=dlng),
        device_status=device,
        number_verified=num_ok,
        sim_swap_recent=sim_swap,
        quality_on_demand_ready=qod,
        congestion_level=congestion,
        inside_geofence=geofence,
    )


def seed_drivers() -> dict[str, DriverProfile]:
    seeds = [
        # Douala
        _drv(101, "Amina N.",   "+237670000101", "MTN Cameroon",     City.douala, 4.0522, 9.7670, 4.0524, 9.7668, "Toyota Yaris",       "CE 421 AB", 4.9, 1284, "#22d3ee", "healthy", True,  False, True,  "low"),
        _drv(102, "Blaise T.",  "+237670000102", "Orange Cameroun",  City.douala, 4.0535, 9.7705, 4.0672, 9.7197, "Hyundai Accent",     "LT 219 CD", 4.6, 612,  "#a78bfa", "healthy", False, False, True,  "moderate"),
        _drv(103, "Chantal E.", "+237670000103", "MTN Cameroon",     City.douala, 4.0492, 9.7601, 4.0501, 9.7610, "Toyota Corolla",     "CE 938 EF", 3.2, 88,   "#f472b6", "suspicious", False, True,  False, "high"),
        _drv(104, "Didier K.",  "+237670000104", "Camtel",           City.douala, 4.0602, 9.7724, 4.0601, 9.7722, "Kia Picanto",        "CE 715 GH", 4.4, 432,  "#fbbf24", "unknown", True,  False, True,  "moderate"),
        _drv(105, "Esther M.", "+237670000105", "MTN Cameroon",     City.douala, 4.0567, 9.7658, 4.0568, 9.7657, "Suzuki Swift",       "CE 110 IJ", 4.8, 921,  "#34d399", "healthy", True,  False, True,  "low"),
        # Yaoundé
        _drv(201, "Florent O.", "+237670000201", "Orange Cameroun",  City.yaounde, 3.8501, 11.5050, 3.8502, 11.5048, "Renault Logan",     "CY 304 KL", 4.7, 540,  "#60a5fa", "healthy", True,  False, True,  "low"),
        _drv(202, "Gisèle P.",  "+237670000202", "MTN Cameroon",     City.yaounde, 3.8460, 11.4995, 3.8702, 11.5380, "Toyota Vitz",       "CY 882 MN", 3.9, 211,  "#fb7185", "healthy", False, False, True,  "moderate"),
        # Lagos
        _drv(301, "Henry A.",  "+2348012345671", "MTN Nigeria",      City.lagos,   6.5260, 3.3811, 6.5258, 3.3812, "Toyota Camry",       "LAG 123 AA", 4.9, 1502, "#22d3ee", "healthy", True,  False, True,  "low"),
        _drv(302, "Ifeoma B.", "+2348012345672", "Airtel Nigeria",   City.lagos,   6.5210, 3.3750, 6.5215, 3.3752, "Honda Accord",       "LAG 444 BB", 4.5, 730,  "#f472b6", "unknown", True,  False, True,  "moderate"),
        _drv(303, "Jide C.",   "+2348012345673", "Glo Nigeria",      City.lagos,   6.5300, 3.3855, 6.5300, 3.3855, "Lexus RX",           "LAG 909 CC", 2.8, 47,   "#ef4444", "suspicious", False, True,  False, "high", geofence=False),
        # Nairobi
        _drv(401, "Kamau D.",  "+254712345671",  "Safaricom",        City.nairobi, -1.2900, 36.8200, -1.2902, 36.8198, "Toyota Axio",     "KDA 123A", 4.8, 1130, "#34d399", "healthy", True,  False, True,  "low"),
        _drv(402, "Lilian E.", "+254712345672",  "Airtel Kenya",     City.nairobi, -1.2950, 36.8260, -1.2960, 36.8270, "Mazda Demio",     "KDB 456B", 4.3, 320,  "#a78bfa", "healthy", True,  False, True,  "moderate"),
        # Dakar
        _drv(501, "Mamadou S.","+221770000501",  "Orange Sénégal",   City.dakar,    14.7180, -17.4690, 14.7181, -17.4690, "Dacia Logan",   "DK 222 CD", 4.7, 980,  "#60a5fa", "healthy", True,  False, True,  "low"),
        _drv(502, "Ndeye F.",  "+221770000502",  "Free Sénégal",     City.dakar,    14.7150, -17.4630, 14.7400, -17.4500, "Hyundai i10",   "DK 778 EF", 3.5, 64,   "#fbbf24", "suspicious", False, True,  False, "high"),
    ]
    return {d.id: d for d in seeds}


DRIVERS: dict[str, DriverProfile] = seed_drivers()
RIDES: dict[str, object] = {}
SUBSCRIPTIONS: dict[str, object] = {}
