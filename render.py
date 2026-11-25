#!/usr/bin/env python3
"""Render the 25 November 2026 world-news front page (1024x1024 PNG).
Deterministic: no randomness, no clock, no network. Written from scratch.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (244, 238, 223)
PANEL_BG = (250, 247, 238)
NAVY = (31, 42, 68)
GOLD = (201, 162, 39)
RED = (176, 30, 36)
INK = (20, 20, 20)
GREY = (90, 86, 76)
BORDER = (70, 64, 52)

REGION_COLORS = {
    "EUROPE": (36, 64, 122),
    "MIDDLE EAST": (140, 32, 32),
    "AFRICA": (196, 110, 20),
    "SOUTH ASIA": (110, 70, 140),
    "EAST ASIA": (16, 110, 110),
    "SE ASIA": (34, 120, 60),
    "AMERICAS": (20, 90, 60),
    "OCEANIA": (60, 100, 140),
    "WORLD": (31, 42, 68),
}

STATUS_COLORS = {
    "CONFIRMED": (34, 120, 60),
    "OFFICIAL": (31, 42, 68),
    "REPORTED": (60, 58, 52),
    "CLAIM": (196, 110, 20),
    "ONGOING": (176, 30, 36),
}

# (number, region, topic, place, headline, deck, source, status, pictogram, lat, lon, pin dx, pin dy, mini-map, big number)
PANELS = [
    (1, "WORLD", "SPACE", "JIUQUAN, CHINA",
     "Shenzhou-24 lifts first foreign astronaut",
     "Long March rocket lifts Tang Hongbo, Wu Yi and Zeeshan Ali to the station; Ali is the first Pakistani in orbit.",
     "Reuters - Xinhua", "CONFIRMED", "rocket", 39.7, 98.5, 0, -11, "china", ""),
    (2, "MIDDLE EAST", "YEMEN", "JEDDAH, SAUDI ARABIA",
     "Houthis threaten Jeddah and all Saudi Red Sea ports",
     "Houthis say Jeddah and every Saudi Red Sea port are targets; the coalition bombs Hodeidah, Saada and Amran.",
     "Reuters - Alhurra", "CLAIM", "missile", 21.5, 39.2, -20, 16, "redsea", ""),
    (3, "EAST ASIA", "ECONOMY", "TOKYO, JAPAN",
     "Japan service prices hit 36-year high",
     "Services PPI up 4.2% in Oct, fastest since 1990; rate-hike case grows.",
     "Reuters - FXStreet", "CONFIRMED", "up", 35.7, 139.7, -6, -20, "japan", ""),
    (4, "AMERICAS", "TRADE", "WASHINGTON, US",
     "US readies tariffs on 16 economies",
     "Duties of 15 to 25% weighed after a Section 301 probe.",
     "AP - Reuters", "REPORTED", "chart", 38.9, -77.0, 0, 0, "", "15-25%"),
    (5, "EAST ASIA", "MARKETS", "SEOUL, SOUTH KOREA",
     "Asian stocks tumble on tariff fears",
     "Korea falls 5.3%, Taiwan 5.1%; Nikkei drops 2.9%.",
     "Reuters - Moneycontrol", "CONFIRMED", "down", 37.5, 127.0, 10, 6, "", "5.3%"),
    (6, "WORLD", "MARKETS", "LONDON, UK",
     "Gold slips to $3,544.54",
     "Gold eases as dollar holds; Dec Fed hike odds at 97%.",
     "Reuters - CNBC-TV18", "CONFIRMED", "chart", 51.5, -0.1, -6, -2, "", "$3,544"),
    (7, "EUROPE", "POLITICS", "STRASBOURG, FRANCE",
     "EU Parliament debates 1.58tn budget",
     "MEPs weigh Costa's revised 2028-34 budget plan.",
     "Europarl - Euronews", "OFFICIAL", "", 48.6, 7.75, 20, -12, "", "1.58tn"),
    (8, "EAST ASIA", "CHINA", "SHANGHAI, CHINA",
     "Shanghai pledges loyalty amid probe",
     "City leaders vow loyalty to Beijing after Chen probe.",
     "Reuters - Jiefang Daily", "REPORTED", "flag", 31.2, 121.5, -3, 18, "", ""),
    (9, "MIDDLE EAST", "LEBANON", "BEIRUT, LEBANON",
     "Hezbollah hits back after Israeli strikes",
     "Hezbollah hits Israeli positions after deadly strikes.",
     "Arab Press - Al Jazeera", "REPORTED", "blast", 33.9, 35.5, -16, -6, "", ""),
    (10, "WORLD", "ENERGY", "STRAIT OF HORMUZ",
     "Oil falls on glut fears",
     "Brent $90.97, WTI $81.58 as glut fears win.",
     "Reuters - BusinessToday", "CONFIRMED", "barrel", 26.5, 56.0, 10, 18, "", ""),
    (11, "OCEANIA", "ECONOMY", "CANBERRA, AUSTRALIA",
     "Australia inflation runs hot",
     "Prices rise more than forecast; core inflation 3.8%.",
     "ABS - Reuters", "OFFICIAL", "up", -35.3, 149.1, -28, -6, "", "3.8%"),
    (12, "WORLD", "RIGHTS", "GENEVA, SWITZERLAND",
     "UN opens 16 Days of Activism",
     "Drive against gender-based violence runs to Dec 10.",
     "UN Women - WHO", "OFFICIAL", "flag", 46.2, 6.1, -2, 20, "", "16"),
    (13, "SOUTH ASIA", "SOCIETY", "NEW DELHI, INDIA",
     "India launches Nayi Chetna 5.0",
     "Fifth edition of the gender campaign opens today.",
     "PIB - YourStory", "OFFICIAL", "mega", 28.6, 77.2, 0, 2, "", "5.0"),
    (14, "EUROPE", "ENERGY", "SIMFEROPOL, CRIMEA",
     "Crimea cuts power 30% for 10 days",
     "Daytime cuts from Nov 25; peak noon to 3pm.",
     "Euromaidan - Devdiscourse", "CONFIRMED", "down", 44.9, 34.1, 12, 14, "", "30%"),
    (15, "SE ASIA", "ENVIRONMENT", "BANGKOK, THAILAND",
     "Thai clean air bill passes House vote",
     "House backs draft 429-0 after seven-year push.",
     "Bangkok Post", "REPORTED", "gavel", 13.8, 100.5, -4, 14, "", "429"),
]

# (number, text, source)
ALSO = [
    (16, "Bitcoin slips 1% to $59,257", "Reuters"),
    (17, "Dollar steady; Fed hike odds 97%", "Reuters"),
    (18, "EU hosts Western Balkans summit", "EU Insider"),
    (19, "US inflation, GDP due 13:30 GMT", "Reuters"),
    (20, "Steinmeier visits Kenya, meets Ruto", "People Daily"),
    (21, "Philippine House okays retirement at 56", "Tribune"),
    (22, "Thai cabinet widens e-withholding tax", "NBT World"),
    (23, "PhilHealth boosts hospital cover 20%", "Tribune"),
    (24, "US supply deal blindsided Phl officials", "Tribune"),
    (25, "Palace rejects Duterte abuse claims", "Bernama"),
    (26, "Pete Edochie dies at 79", "Punch - GhanaWeb"),
    (27, "Egypt urged to reopen Mada Masr", "Amnesty - AllAfrica"),
    (28, "Delhi air poor, AQI 200", "weather.com"),
    (29, "Iran to execute two men at dawn", "Iran FFM"),
    (30, "UNRWA worker, Hamas security chief killed", "Particle"),
    (31, "IDF hits Beirut, targets Hezbollah commander", "JPost"),
    (32, "Ukraine asks allies for 40 jets", "Euromaidan Press"),
    (33, "55,000 petitions in occupied eastern Ukraine", "Euromaidan"),
    (34, "EU nature-law talks resume before vote", "EU Parliament"),
    (35, "Digital scams hit 77% of Kenyans", "TransUnion"),
    (36, "M5.9 quake hits Balleny Islands", "USGS"),
    (37, "Duterte fights ICC witness secrecy", "Tribune"),
]

# region per ALSO item, same order as ALSO (for region-coloured numbers)
ALSO_REGIONS = [
    "WORLD", "WORLD", "EUROPE", "AMERICAS", "AFRICA",
    "SE ASIA", "SE ASIA", "SE ASIA", "SE ASIA", "SE ASIA",
    "AFRICA", "AFRICA", "SOUTH ASIA", "MIDDLE EAST", "MIDDLE EAST",
    "MIDDLE EAST", "EUROPE", "EUROPE", "EUROPE", "AFRICA",
    "OCEANIA", "SE ASIA",
]

# (big number, caption)
NUMBERS = [
    ("16", "economies facing new US tariffs"),
    ("55,000", "sign petitions in occupied eastern Ukraine"),
    ("4.2%", "Japan services prices rise"),
    ("$59,257", "Bitcoin price, down 1%"),
    ("3.8%", "Australia core inflation"),
    ("30%", "Crimea power cut for 10 days"),
    ("429", "votes for Thai clean air bill"),
]

# (UTC time, event) - spread across the strip. The 00:18-00:30 cluster
# keeps only two events: Gold $3,544.54 and Japan PPI +4.2% were
# dropped because both already appear on the page (P6 deck / P3 deck
# and the numbers panel). The two cluster events are drawn JOINED on
# one line below the axis ("Shenzhou lifts off · Australia CPI 3.8%")
# so every event label on the strip shares ONE baseline.
TIMELINE = [
    ("00:18", "Shenzhou lifts off"),
    ("00:30", "Australia CPI 3.8%"),
    ("05:00", "Crimea cuts begin"),
    ("09:15", "EP budget debate"),
    ("13:30", "US data (sched.)"),
    ("17:45", "UCL (sched.)"),
]

LEFT_OUT = ("Left out because they happened on an earlier day: "
            "Tue 24 Nov: Hustler Fund boost - Cikande toll 26 - Bamburi cement plant - "
            "WHO Ebola pullout - UK Houthi sanctions - Iraq oil seizure - Gaza strikes - "
            "Iran drug shortage - Gaza toll 483 - Amnesty Tigray - "
            "Mon 23 Nov: Lebanon 2 killed - 30 Oct: Germany GDP detail")

REGION_COUNTS = [("EUROPE", 6), ("MIDDLE EAST", 5), ("AFRICA", 4), ("SOUTH ASIA", 2),
                 ("EAST ASIA", 3), ("SE ASIA", 7), ("AMERICAS", 2), ("OCEANIA", 2),
                 ("WORLD", 6)]


def font(path, size):
    return ImageFont.truetype(path, size)


SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def wrap(text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(text, fnt, max_w, max_lines):
    """Wrap text, hard-truncating to max_lines with no mid-word cut."""
    lines = wrap(text, fnt, max_w)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        # trim last line so it fits with an ellipsis-free cut at a word boundary
        while lines and fnt.getlength(lines[-1]) > max_w:
            lines[-1] = lines[-1].rsplit(" ", 1)[0] if " " in lines[-1] else ""
        lines = [l for l in lines if l]
    return lines

def star_points(cx, cy, r_out, r_in, n=5):
    import math
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(-90 + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# flag of the story's primary country, per panel number (P7 is the EU,
# P10/P12 are world/UN stories, P14 Crimea uses the Ukrainian flag;
# P2 flies the Saudi flag for its location line "JEDDAH, SAUDI ARABIA"
# though the story is the Houthi/Yemen side, named in its region line)
PANEL_FLAGS = ["CN", "SA", "JP", "US", "KR", "GB", "EU", "CN", "LB", "UN",
               "AU", "UN", "IN", "UA", "TH"]


def draw_flag(d, code, x, y, w, h):
    """Small simplified but recognisable flag chip, PIL only."""
    def X(u):
        return x + u * w
    def Y(v):
        return y + v * h
    if code == "CN":
        d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
        d.polygon(star_points(X(0.30), Y(0.38), h * 0.26, h * 0.11), fill=(255, 222, 0))
        for (su, sv) in [(0.58, 0.18), (0.68, 0.30), (0.68, 0.48), (0.58, 0.60)]:
            sx, sy = X(su), Y(sv)
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 222, 0))
    elif code == "SA":
        # Saudi Arabia: green field, white shahada band above, white
        # sword below (script suggested as a band at this size)
        d.rectangle([x, y, x + w, y + h], fill=(0, 106, 78))
        d.line([X(0.20), Y(0.28), X(0.80), Y(0.28)], fill=(255, 255, 255), width=2)
        d.line([X(0.32), Y(0.28), X(0.32), Y(0.18)], fill=(255, 255, 255), width=1)
        d.line([X(0.56), Y(0.28), X(0.56), Y(0.18)], fill=(255, 255, 255), width=1)
        d.line([X(0.18), Y(0.68), X(0.82), Y(0.68)], fill=(255, 255, 255), width=2)
        d.line([X(0.18), Y(0.60), X(0.18), Y(0.76)], fill=(255, 255, 255), width=2)
    elif code == "YE":
        for i, c in enumerate([(206, 17, 38), (255, 255, 255), (0, 0, 0)]):
            d.rectangle([x, Y(i / 3), x + w, Y((i + 1) / 3)], fill=c)
    elif code == "JP":
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        d.ellipse([X(0.5) - h * 0.30, Y(0.5) - h * 0.30,
                   X(0.5) + h * 0.30, Y(0.5) + h * 0.30], fill=(188, 0, 45))
    elif code == "US":
        for i in range(7):
            c = (178, 34, 52) if i % 2 == 0 else (255, 255, 255)
            d.rectangle([x, Y(i / 7), x + w, Y((i + 1) / 7)], fill=c)
        d.rectangle([x, y, X(0.42), Y(4 / 7)], fill=(60, 59, 110))
        for (su, sv) in [(0.10, 0.14), (0.26, 0.14), (0.10, 0.32), (0.26, 0.32), (0.18, 0.46)]:
            sx, sy = X(su), Y(sv)
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    elif code == "KR":
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        d.ellipse([X(0.5) - h * 0.30, Y(0.5) - h * 0.30,
                   X(0.5) + h * 0.30, Y(0.5) + h * 0.30], fill=(205, 49, 60))
        d.pieslice([X(0.5) - h * 0.30, Y(0.5) - h * 0.30,
                    X(0.5) + h * 0.30, Y(0.5) + h * 0.30], 0, 180, fill=(0, 56, 147))
        for (su, sv) in [(0.10, 0.12), (0.84, 0.12), (0.10, 0.80), (0.84, 0.80)]:
            d.rectangle([X(su), Y(sv), X(su) + 3, Y(sv) + 1], fill=(0, 0, 0))
    elif code == "GB":
        d.rectangle([x, y, x + w, y + h], fill=(0, 36, 125))
        d.line([x, y, x + w, y + h], fill=(255, 255, 255), width=2)
        d.line([x, y + h, x + w, y], fill=(255, 255, 255), width=2)
        d.line([x, y, x + w, y + h], fill=(207, 20, 43), width=1)
        d.line([x, y + h, x + w, y], fill=(207, 20, 43), width=1)
        d.rectangle([X(0.42), y, X(0.58), y + h], fill=(255, 255, 255))
        d.rectangle([x, Y(0.38), x + w, Y(0.62)], fill=(255, 255, 255))
        d.rectangle([X(0.46), y, X(0.54), y + h], fill=(207, 20, 43))
        d.rectangle([x, Y(0.44), x + w, Y(0.56)], fill=(207, 20, 43))
    elif code == "EU":
        d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
        import math
        for i in range(12):
            a = math.radians(i * 30 - 90)
            sx, sy = X(0.5) + h * 0.30 * math.cos(a), Y(0.5) + h * 0.30 * math.sin(a)
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 209, 0))
    elif code == "LB":
        for (v0, v1, c) in [(0, 0.25, (237, 41, 47)), (0.25, 0.75, (255, 255, 255)),
                            (0.75, 1.0, (237, 41, 47))]:
            d.rectangle([x, Y(v0), x + w, Y(v1)], fill=c)
        d.polygon([(X(0.5), Y(0.32)), (X(0.62), Y(0.62)), (X(0.38), Y(0.62))],
                  fill=(0, 122, 61))
        d.rectangle([X(0.48), Y(0.62), X(0.52), Y(0.70)], fill=(0, 122, 61))
    elif code == "UN":
        d.rectangle([x, y, x + w, y + h], fill=(91, 155, 213))
        d.ellipse([X(0.5) - h * 0.30, Y(0.5) - h * 0.30,
                   X(0.5) + h * 0.30, Y(0.5) + h * 0.30], fill=(255, 255, 255))
        d.ellipse([X(0.5) - 1, Y(0.5) - 1, X(0.5) + 1, Y(0.5) + 1], fill=(91, 155, 213))
    elif code == "AU":
        d.rectangle([x, y, x + w, y + h], fill=(0, 36, 125))
        d.rectangle([X(0.44), y, X(0.50), Y(0.5)], fill=(255, 255, 255))
        d.rectangle([x, Y(0.22), X(0.5), Y(0.28)], fill=(255, 255, 255))
        d.rectangle([X(0.46), y, X(0.48), Y(0.5)], fill=(207, 20, 43))
        d.rectangle([x, Y(0.24), X(0.5), Y(0.26)], fill=(207, 20, 43))
        d.polygon(star_points(X(0.25), Y(0.75), h * 0.18, h * 0.08), fill=(255, 255, 255))
        for (su, sv) in [(0.68, 0.25), (0.82, 0.42), (0.66, 0.60), (0.86, 0.72)]:
            sx, sy = X(su), Y(sv)
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
    elif code == "IN":
        for i, c in enumerate([(255, 153, 51), (255, 255, 255), (19, 136, 8)]):
            d.rectangle([x, Y(i / 3), x + w, Y((i + 1) / 3)], fill=c)
        d.ellipse([X(0.5) - h * 0.15, Y(0.5) - h * 0.15,
                   X(0.5) + h * 0.15, Y(0.5) + h * 0.15], outline=(0, 0, 128))
        d.ellipse([X(0.5) - 1, Y(0.5) - 1, X(0.5) + 1, Y(0.5) + 1], fill=(0, 0, 128))
    elif code == "TH":
        for (v0, v1, c) in [(0, 1 / 6, (165, 25, 49)), (1 / 6, 2 / 6, (244, 245, 248)),
                            (2 / 6, 4 / 6, (45, 42, 74)), (4 / 6, 5 / 6, (244, 245, 248)),
                            (5 / 6, 1.0, (165, 25, 49))]:
            d.rectangle([x, Y(v0), x + w, Y(v1)], fill=c)
    elif code == "UA":
        d.rectangle([x, y, x + w, Y(0.5)], fill=(0, 91, 187))
        d.rectangle([x, Y(0.5), x + w, y + h], fill=(255, 213, 0))
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=(50, 48, 44))


def draw_pic(d, kind, x, y, w, h, dark):
    """Draw a flat pictogram inside box (x, y, w, h) on a dark band."""
    cx, cy = x + w // 2, y + h // 2
    white = (240, 240, 235)
    yellow = (230, 190, 60)
    red = (200, 60, 50)
    green = (90, 170, 100)
    blue = (110, 170, 220)
    if kind == "rocket":
        d.polygon([(cx, y + 4), (cx + 9, cy + 6), (cx - 9, cy + 6)], fill=white)
        d.rectangle([cx - 9, cy + 4, cx + 9, cy + 16], fill=white)
        d.polygon([(cx - 9, cy + 8), (cx - 16, cy + 18), (cx - 9, cy + 16)], fill=red)
        d.polygon([(cx + 9, cy + 8), (cx + 16, cy + 18), (cx + 9, cy + 16)], fill=red)
        d.polygon([(cx - 4, cy + 16), (cx + 4, cy + 16), (cx, cy + 26)], fill=yellow)
        d.ellipse([x + 6, y + 6, x + 16, y + 16], fill=yellow)
        d.ellipse([x + w - 16, cy - 4, x + w - 6, cy + 6], fill=white)
    elif kind == "missile":
        d.rectangle([cx - 18, cy - 4, cx + 14, cy + 4], fill=white)
        d.polygon([(cx + 14, cy - 4), (cx + 24, cy), (cx + 14, cy + 4)], fill=red)
        d.polygon([(cx - 18, cy - 4), (cx - 26, cy - 12), (cx - 18, cy)], fill=white)
        d.polygon([(cx - 18, cy + 4), (cx - 26, cy + 12), (cx - 18, cy)], fill=white)
        d.line([x + 4, cy + 14, x + w - 4, cy + 14], fill=yellow, width=2)
        for i in range(5):
            d.line([x + 6 + i * 8, cy + 14, x + 2 + i * 8, cy + 20], fill=yellow, width=2)
    elif kind == "cross":
        d.rectangle([x + 6, y + 6, x + w - 6, y + h - 6], fill=white)
        d.rectangle([cx - 5, y + 12, cx + 5, y + h - 12], fill=red)
        d.rectangle([cx - 12, cy - 5, cx + 12, cy + 5], fill=red)
    elif kind == "chart":
        d.rectangle([x + 8, cy + 2, x + w - 8, cy + 4], fill=white)
        pts = [(x + 10, cy - 8), (x + 22, cy - 14), (x + 34, cy - 6), (x + 46, cy - 16), (x + 58, cy - 10)]
        d.line(pts, fill=yellow, width=3)
        for p in pts:
            d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=yellow)
        d.rectangle([x + 10, cy + 8, x + 16, cy + 18], fill=green)
        d.rectangle([x + 22, cy + 4, x + 28, cy + 18], fill=green)
        d.rectangle([x + 34, cy + 10, x + 40, cy + 18], fill=green)
    elif kind == "down":
        d.rectangle([x + 8, cy + 2, x + w - 8, cy + 4], fill=white)
        pts = [(x + 10, cy - 16), (x + 22, cy - 8), (x + 34, cy - 12), (x + 46, cy - 2), (x + 58, cy + 6)]
        d.line(pts, fill=red, width=3)
        for p in pts:
            d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=red)
        d.polygon([(x + w - 16, cy + 10), (x + w - 6, cy + 10), (x + w - 11, cy + 20)], fill=red)
    elif kind == "up":
        d.rectangle([x + 8, cy + 2, x + w - 8, cy + 4], fill=white)
        pts = [(x + 10, cy + 8), (x + 22, cy + 2), (x + 34, cy + 6), (x + 46, cy - 8), (x + 58, cy - 14)]
        d.line(pts, fill=green, width=3)
        for p in pts:
            d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=green)
        d.polygon([(x + w - 16, cy - 14), (x + w - 6, cy - 14), (x + w - 11, cy - 22)], fill=green)
    elif kind == "gavel":
        d.line([cx - 16, cy - 10, cx + 16, cy + 10], fill=white, width=6)
        d.rectangle([cx - 22, cy - 16, cx - 8, cy - 6], fill=yellow)
        d.rectangle([cx + 8, cy + 6, cx + 22, cy + 16], fill=yellow)
        d.rectangle([cx - 20, cy + 14, cx + 20, cy + 18], fill=white)
    elif kind == "derrick":
        d.polygon([(cx - 14, cy + 18), (cx - 4, cy - 16), (cx + 4, cy - 16), (cx + 14, cy + 18)], outline=white, width=3)
        d.line([cx - 10, cy + 6, cx + 10, cy + 6], fill=white, width=2)
        d.line([cx - 7, cy - 4, cx + 7, cy - 4], fill=white, width=2)
        d.line([cx, cy - 16, cx + 16, cy - 26], fill=yellow, width=3)
        d.ellipse([cx + 14, cy - 30, cx + 22, cy - 22], fill=yellow)
    elif kind == "flag":
        d.line([cx - 12, y + 6, cx - 12, y + h - 8], fill=white, width=3)
        d.polygon([(cx - 12, y + 6), (cx + 18, y + 12), (cx - 12, y + 20)], fill=red)
        d.ellipse([cx - 15, y + 2, cx - 9, y + 8], fill=yellow)
    elif kind == "mega":
        d.polygon([(cx - 14, cy - 8), (cx + 16, cy - 18), (cx + 16, cy + 18), (cx - 14, cy + 8)], fill=white)
        d.rectangle([cx - 22, cy + 2, cx - 12, cy + 18], fill=yellow)
        d.arc([cx + 20, cy - 12, cx + 32, cy + 12], -60, 60, fill=yellow, width=2)
        d.arc([cx + 26, cy - 16, cx + 40, cy + 16], -60, 60, fill=yellow, width=2)
    elif kind == "blast":
        for ang, ln in [(0, 22), (45, 18), (90, 24), (135, 18), (180, 22), (225, 18), (270, 24), (315, 18)]:
            import math
            a = math.radians(ang)
            d.line([cx, cy, cx + int(ln * math.cos(a)), cy + int(ln * math.sin(a))], fill=yellow, width=3)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=red)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=white)
    elif kind == "barrel":
        d.ellipse([cx - 14, cy - 18, cx + 14, cy - 10], fill=blue)
        d.rectangle([cx - 14, cy - 14, cx + 14, cy + 14], fill=blue)
        d.ellipse([cx - 14, cy + 10, cx + 14, cy + 18], fill=(70, 130, 190))
        d.rectangle([cx - 14, cy - 2, cx + 14, cy + 2], fill=(70, 130, 190))
        d.text((cx - 6, cy - 20), "$", font=font(SANS_B, 13), fill=white)
    elif kind == "pill":
        d.rounded_rectangle([cx - 20, cy - 8, cx + 20, cy + 8], radius=8, fill=white)
        d.ellipse([cx - 14, cy - 5, cx - 4, cy + 5], fill=red)
        d.ellipse([cx + 4, cy - 5, cx + 14, cy + 5], fill=blue)
    elif kind == "fence":
        for i, fx in enumerate([x + 8, cx - 14, cx + 6, x + w - 16]):
            d.line([fx, y + 6, fx, y + h - 8], fill=white, width=3)
        d.line([x + 4, cy - 6, x + w - 4, cy - 6], fill=yellow, width=3)
        d.line([x + 4, cy + 8, x + w - 4, cy + 8], fill=yellow, width=3)
    elif kind == "ship":
        d.rectangle([cx - 20, cy - 2, cx + 20, cy + 8], fill=white)
        d.polygon([(cx - 20, cy - 2), (cx + 20, cy - 2), (cx + 12, cy + 10), (cx - 12, cy + 10)], fill=(150, 150, 145))
        d.rectangle([cx - 4, cy - 16, cx + 4, cy - 2], fill=white)
        d.rectangle([cx - 10, cy - 12, cx + 10, cy - 8], fill=red)
        d.line([x + 4, cy + 16, x + w - 4, cy + 16], fill=blue, width=2)
        d.line([x + 10, cy + 20, x + w - 10, cy + 20], fill=blue, width=2)
    elif kind == "ape":
        d.ellipse([cx - 14, cy - 12, cx + 14, cy + 12], fill=(150, 100, 60))
        d.ellipse([cx - 10, cy - 2, cx - 2, cy + 8], fill=(210, 180, 140))
        d.ellipse([cx + 2, cy - 2, cx + 10, cy + 8], fill=(210, 180, 140))
        d.ellipse([cx - 5, cy - 8, cx - 1, cy - 4], fill=INK)
        d.ellipse([cx + 1, cy - 8, cx + 5, cy - 4], fill=INK)
        d.ellipse([cx - 18, cy - 16, cx - 10, cy - 6], fill=(150, 100, 60))
        d.ellipse([cx + 10, cy - 16, cx + 18, cy - 6], fill=(150, 100, 60))
        d.ellipse([x + 4, cy + 12, x + 12, cy + 20], fill=green)
        d.ellipse([x + w - 12, cy + 12, x + w - 4, cy + 20], fill=green)


def map_label(d, lx, ly, text):
    """White text on a small navy chip, readable on sea or land."""
    f = font(SANS_B, 8)
    tw = f.getlength(text)
    d.rectangle([lx - 2, ly - 1, lx + tw + 2, ly + 10], fill=NAVY)
    d.text((lx, ly), text, font=f, fill=(255, 255, 255))


def gold_pill(d, lx, ly, text):
    """Dark text on a small gold pill, for data badges inside maps."""
    f = font(SANS_B, 8)
    tw = f.getlength(text)
    d.rounded_rectangle([lx, ly, lx + tw + 8, ly + 13], radius=3, fill=GOLD)
    d.text((lx + 4, ly + 2), text, font=f, fill=NAVY)


def vgrad(d, x, y, w, h, c_top, c_bot, steps=16):
    """Deterministic vertical gradient: fill rect with interpolated strips."""
    for i in range(steps):
        t0 = i / steps
        t1 = (i + 1) / steps
        c = tuple(int(c_top[k] + (c_bot[k] - c_top[k]) * (t0 + t1) / 2) for k in range(3))
        d.rectangle([x, y + int(t0 * h), x + w, y + int(t1 * h)], fill=c)


def draw_mini_map(d, kind, x, y, w, h):
    """Scene strip inside a hero panel's navy band.
    A drawn scene per story (launch site, sea, city skyline), with the
    story-number badge drawn over the top-left corner afterwards."""
    sea = (38, 62, 100)
    land = (205, 190, 150)
    d.rectangle([x, y, x + w, y + h], fill=sea)

    def P(u, v):
        return (x + u * w, y + v * h)

    if kind == "china":
        # Jiuquan launch site at dawn: indigo sky, warm horizon, desert
        # ground, gantry, Long March rocket lifting off with smoke.
        vgrad(d, x, y, w, int(h * 0.68), (26, 40, 84), (228, 158, 74))
        d.rectangle([x, y + int(h * 0.68), x + w, y + h], fill=land)
        d.line([P(0.0, 0.68), P(0.30, 0.64), P(0.62, 0.69), P(1.0, 0.65)],
               fill=(178, 160, 122), width=2)
        # stars, kept clear of the top-right status-pill zone
        for (su, sv) in [(0.06, 0.12), (0.14, 0.05), (0.24, 0.10), (0.34, 0.06),
                         (0.44, 0.13), (0.52, 0.05), (0.60, 0.16), (0.10, 0.22)]:
            sx, sy = P(su, sv)
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
        # launch gantry left of the rocket
        gx0, gx1 = P(0.28, 0)[0], P(0.36, 0)[0]
        gy_top, gy_bot = P(0, 0.22)[1], P(0, 0.68)[1]
        d.line([gx0, gy_top, gx0, gy_bot], fill=(70, 70, 80), width=3)
        d.line([gx1, gy_top, gx1, gy_bot], fill=(70, 70, 80), width=3)
        for i in range(6):
            yy = gy_top + i * (gy_bot - gy_top) // 5
            d.line([gx0, yy, gx1, yy], fill=(70, 70, 80), width=2)
        # rocket: white body, red nose + fins, lifting off
        rx0, rx1 = P(0.40, 0)[0], P(0.45, 0)[0]
        ry_top, ry_bot = P(0, 0.20)[1], P(0, 0.58)[1]
        rmid = (rx0 + rx1) / 2
        d.polygon([(rx0, ry_top + 8), (rmid, ry_top - 2), (rx1, ry_top + 8)],
                  fill=(200, 60, 50))
        d.rectangle([rx0, ry_top + 8, rx1, ry_bot], fill=(240, 240, 235))
        d.polygon([(rx0, ry_bot - 8), (rx0 - 6, ry_bot + 2), (rx0, ry_bot)], fill=(200, 60, 50))
        d.polygon([(rx1, ry_bot - 8), (rx1 + 6, ry_bot + 2), (rx1, ry_bot)], fill=(200, 60, 50))
        d.ellipse([rmid - 3, ry_top + 14, rmid + 3, ry_top + 20], fill=(38, 62, 100))
        # flame + smoke plume at the base
        d.polygon([(rmid - 5, ry_bot), (rmid + 5, ry_bot), (rmid, ry_bot + 10)],
                  fill=(230, 190, 60))
        for (su, sv, sr) in [(0.33, 0.70, 9), (0.42, 0.74, 12), (0.52, 0.70, 10),
                             (0.38, 0.78, 8), (0.48, 0.80, 9)]:
            sx, sy = P(su, sv)
            d.ellipse([sx - sr, sy - sr // 2, sx + sr, sy + sr // 2], fill=(235, 235, 230))
        d.text((x + 38, y + 6), "00:18 UTC · 25 NOV", font=font(SANS_B, 8), fill=GOLD)
        map_label(d, *P(0.72, 0.80), "JIUQUAN")
        gold_pill(d, x + 6, y + h - 17, "1ST PAKISTANI IN ORBIT")
    elif kind == "redsea":
        # Red Sea at day: pale sky, blue sea, two coastlines, a navy
        # ship in the channel and a container port at Jeddah.
        vgrad(d, x, y, w, int(h * 0.16), (196, 208, 226), (238, 226, 200))
        d.rectangle([x, y + int(h * 0.16), x + w, y + h], fill=sea)
        # wave lines, all inside the sea channel
        for (wu, wv, wl) in [(0.30, 0.30, 0.10), (0.36, 0.55, 0.08), (0.30, 0.80, 0.12),
                             (0.44, 0.28, 0.08), (0.40, 0.70, 0.10)]:
            wx, wy = P(wu, wv)
            d.line([wx, wy, wx + wl * w, wy], fill=(120, 160, 210), width=1)
        africa = [(0.02, 0.16), (0.22, 0.16), (0.28, 0.30), (0.24, 0.50), (0.20, 0.68),
                  (0.14, 0.86), (0.05, 0.96), (0.02, 0.60)]
        arabia = [(0.55, 0.16), (0.72, 0.16), (0.95, 0.20), (0.98, 0.40), (0.92, 0.58),
                  (0.82, 0.72), (0.70, 0.86), (0.60, 0.76), (0.55, 0.56), (0.52, 0.36)]
        d.polygon([P(u, v) for u, v in africa], fill=land, outline=(255, 255, 255), width=2)
        d.polygon([P(u, v) for u, v in arabia], fill=land, outline=(255, 255, 255), width=2)
        # coast labels so the two shores cannot be confused
        d.text(P(0.36, 0.68), "RED SEA", font=font(SANS_B, 8), fill=(220, 230, 245))
        d.text(P(0.07, 0.45), "AFRICA", font=font(SANS_B, 8), fill=(70, 64, 52))
        d.text(P(0.66, 0.24), "SAUDI ARABIA", font=font(SANS_B, 8), fill=(70, 64, 52))
        map_label(d, *P(0.66, 0.66), "YEMEN")
        # navy ship in the channel, heading right
        sx0, sx1 = P(0.30, 0)[0], P(0.48, 0)[0]
        sy = P(0, 0.58)[1]
        d.polygon([(sx0, sy), (sx1 - 8, sy), (sx1, sy + 6), (sx0 + 4, sy + 6)],
                  fill=(150, 150, 145))
        d.rectangle([sx0 + 8, sy - 10, sx0 + 26, sy], fill=(230, 230, 225))
        d.line([sx0 + 16, sy - 18, sx0 + 16, sy - 10], fill=(230, 230, 225), width=2)
        d.polygon([(sx0 + 16, sy - 18), (sx0 + 26, sy - 15), (sx0 + 16, sy - 12)],
                  fill=(200, 60, 50))
        d.line([sx0 - 14, sy + 8, sx0, sy + 8], fill=(200, 220, 240), width=1)
        d.line([sx0 - 10, sy + 11, sx0 + 2, sy + 11], fill=(200, 220, 240), width=1)
        # container port on the Jeddah coast + pier into the sea
        for (cu, cv, cc) in [(0.60, 0.50, (200, 60, 50)), (0.65, 0.50, (60, 100, 180)),
                             (0.70, 0.50, (230, 190, 60)), (0.62, 0.56, (90, 170, 100)),
                             (0.67, 0.56, (200, 60, 50))]:
            cx, cy = P(cu, cv)
            d.rectangle([cx, cy, cx + 10, cy + 6], fill=cc, outline=(255, 255, 255))
        d.line([P(0.56, 0.53), P(0.50, 0.53)], fill=(90, 85, 75), width=3)
        jx, jy = P(0.57, 0.42)
        d.ellipse([jx - 4, jy - 4, jx + 4, jy + 4], fill=RED, outline=(255, 255, 255), width=1)
        map_label(d, *P(0.60, 0.36), "JEDDAH")
        # Hodeidah, Saada and Amran: the three Yemeni targets named in
        # the deck — dots sit just inland of Yemen's Red Sea coast
        # (south-west Arabia), NOT on the Saudi side by Jeddah
        for (u, v) in [(0.59, 0.70), (0.60, 0.60), (0.585, 0.65)]:
            hx, hy = P(u, v)
            d.ellipse([hx - 3, hy - 3, hx + 3, hy + 3], fill=RED, outline=(255, 255, 255), width=1)
        map_label(d, *P(0.44, 0.82), "HODEIDAH - SAADA - AMRAN")
    elif kind == "japan":
        # Tokyo at dusk: indigo sky, warm horizon, skyline with lit
        # windows, a Skytree-style tower, and a rising stock chart.
        vgrad(d, x, y, w, int(h * 0.62), (24, 32, 72), (235, 150, 70))
        d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(18, 20, 34))
        for (su, sv) in [(0.08, 0.08), (0.18, 0.05), (0.30, 0.10), (0.42, 0.06),
                         (0.52, 0.12), (0.58, 0.05)]:
            sx, sy = P(su, sv)
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=(255, 255, 255))
        # tower (Skytree) behind the skyline
        tx = P(0.63, 0)[0]
        ty_base, ty_top = P(0, 0.80)[1], P(0, 0.10)[1]
        d.line([(tx - 7, ty_base), (tx, ty_top)], fill=(220, 220, 215), width=3)
        d.line([(tx + 7, ty_base), (tx, ty_top)], fill=(220, 220, 215), width=3)
        for i in range(1, 6):
            yy = ty_base - i * (ty_base - ty_top) // 6
            half = 7 * (yy - ty_top) / (ty_base - ty_top)
            d.line([tx - half, yy, tx + half, yy], fill=(220, 220, 215), width=1)
        d.ellipse([tx - 3, ty_top - 3, tx + 3, ty_top + 3], fill=(200, 60, 50))
        # skyline silhouettes with lit windows
        buildings = [(0.02, 0.12, 0.55), (0.13, 0.22, 0.48), (0.24, 0.32, 0.60),
                     (0.34, 0.44, 0.50), (0.46, 0.56, 0.62), (0.58, 0.68, 0.52),
                     (0.70, 0.80, 0.58), (0.82, 0.92, 0.50), (0.93, 0.99, 0.62)]
        for (bu0, bu1, btop) in buildings:
            bx0, bx1 = P(bu0, 0)[0], P(bu1, 0)[0]
            by = P(0, btop)[1]
            d.rectangle([bx0, by, bx1, P(0, 0.80)[1]], fill=(16, 18, 32))
            for wx in range(int(bx0) + 4, int(bx1) - 3, 7):
                for wy in range(int(by) + 5, int(P(0, 0.80)[1]) - 4, 9):
                    if (wx * 7 + wy * 3) % 5 < 2:
                        d.rectangle([wx, wy, wx + 2, wy + 2], fill=(230, 190, 60))
        # rising stock chart over the skyline
        pts = [P(u, v) for u, v in [(0.05, 0.72), (0.18, 0.66), (0.30, 0.68),
                                    (0.45, 0.55), (0.60, 0.58), (0.75, 0.42),
                                    (0.88, 0.36), (0.97, 0.28)]]
        d.line(pts, fill=(230, 190, 60), width=3)
        for p in pts:
            d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=(230, 190, 60))
        tx2, ty2 = P(0.63, 0.44)
        d.ellipse([tx2 - 4, ty2 - 4, tx2 + 4, ty2 + 4], fill=RED, outline=(255, 255, 255), width=1)
        map_label(d, *P(0.66, 0.40), "TOKYO")
        gold_pill(d, x + w - 84, y + h - 17, "36-YEAR HIGH")


def draw_small_scene(d, num, x, y, w, h):
    """Mini-scene for a small panel's band (about 151x40 px): background,
    subject and one detail, drawn as a real scene of the story's event
    in the 22 Nov winner's style, not a flat pictogram. The red number
    badge (top-left) and the status pill (top-right) are drawn over the
    scene afterwards, and a small number accent (if any) sits on a navy
    chip in the bottom-right corner, so each scene keeps its subject
    clear of that corner and the top strip as sky."""
    def P(u, v):
        return (x + u * w, y + v * h)

    sky = (210, 222, 238)
    white = (240, 240, 235)
    grey = (120, 124, 132)

    if num == 4:
        # Washington: a tariff notice board on the White House lawn.
        # The board stands left of centre, clear of the small number
        # chip in the bottom-right corner; the flagpole is mid-band.
        d.rectangle([x, y, x + w, y + h], fill=sky)
        d.rectangle([x, P(0, 0.62)[1], x + w, y + h], fill=(96, 160, 96))
        d.line([P(0.44, 0)[0], P(0, 0.30)[1], P(0.44, 0)[0], P(0, 0.06)[1]], fill=grey, width=2)
        d.polygon([(P(0.44, 0)[0], P(0, 0.06)[1]), (P(0.44, 0)[0] + 10, P(0, 0.09)[1]),
                   (P(0.44, 0)[0], P(0, 0.12)[1])], fill=RED)
        bx0, bx1 = P(0.10, 0)[0], P(0.38, 0)[0]
        by0, by1 = P(0, 0.50)[1], P(0, 0.88)[1]
        d.rectangle([bx0, by0, bx1, by1], fill=white, outline=NAVY)
        d.rectangle([bx0, by0, bx1, by0 + 7], fill=RED)
        for ly in [0.62, 0.70, 0.78]:
            d.line([bx0 + 5, P(0, ly)[1], bx1 - 5, P(0, ly)[1]], fill=(150, 150, 145), width=1)
        sx, sy = P(0.32, 0)[0], P(0, 0.82)[1]
        d.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=RED)
    elif num == 5:
        # Exchange floor: a falling red line over a dark board
        d.rectangle([x, y, x + w, y + h], fill=(18, 20, 34))
        d.line([x, P(0, 0.30)[1], x + w, P(0, 0.30)[1]], fill=(60, 64, 80), width=1)
        d.line([x, P(0, 0.65)[1], x + w, P(0, 0.65)[1]], fill=(60, 64, 80), width=1)
        # falling line ends well clear of the "5.3%" corner chip,
        # with a down-arrow at its tip
        pts = [P(u, v) for u, v in [(0.04, 0.22), (0.20, 0.34), (0.36, 0.28),
                                    (0.52, 0.52), (0.60, 0.66)]]
        d.line(pts, fill=(200, 60, 50), width=3)
        for p in pts:
            d.ellipse([p[0] - 2, p[1] - 2, p[0] + 2, p[1] + 2], fill=(200, 60, 50))
        ex, ey = pts[-1]
        d.polygon([(ex - 5, ey - 3), (ex + 5, ey - 1), (ex - 1, ey + 7)], fill=(200, 60, 50))
        # three ticker bars under the line, all left of the corner chip
        for (bu, bv, bh) in [(0.40, 0.70, 0.14), (0.48, 0.76, 0.10),
                             (0.56, 0.80, 0.07)]:
            d.rectangle([P(bu, 0)[0], P(0, bv)[1], P(bu, 0)[0] + 7, P(0, bv + bh)[1]],
                        fill=(200, 60, 50))
    elif num == 6:
        # Gold vault: stacked bars on a dark vault floor
        d.rectangle([x, y, x + w, y + h], fill=(32, 28, 40))
        d.ellipse([P(0.42, 0)[0] - 20, P(0, 0.10)[1], P(0.42, 0)[0] + 20, P(0, 0.75)[1]],
                  fill=(70, 58, 30))
        gold = (230, 190, 60)
        edge = (180, 140, 40)

        def bar(u0, v0, u1, v1):
            d.polygon([P(u0, v1), P(u1, v1), P(u1 - 0.03, v0), P(u0 + 0.03, v0)],
                      fill=gold, outline=edge)
        bar(0.26, 0.62, 0.40, 0.78)
        bar(0.42, 0.62, 0.56, 0.78)
        bar(0.34, 0.44, 0.48, 0.60)
        for (cu, cv) in [(0.14, 0.72), (0.14, 0.62), (0.14, 0.52)]:
            cx, cy = P(cu, cv)
            d.ellipse([cx - 8, cy - 3, cx + 8, cy + 3], fill=gold, outline=edge)
    elif num == 7:
        # Strasbourg hemicycle: curved rows of seats under EU blue
        d.rectangle([x, y, x + w, y + h], fill=(36, 64, 122))
        seat = (210, 215, 225)
        for (row_v, u0, u1, n) in [(0.28, 0.30, 0.56, 5), (0.48, 0.24, 0.60, 7),
                                   (0.68, 0.14, 0.60, 8)]:
            for i in range(n):
                sx = P(u0 + (u1 - u0) * i / (n - 1), 0)[0]
                sy = P(0, row_v)[1]
                d.rectangle([sx - 3, sy - 3, sx + 3, sy + 3], fill=seat)
        d.rectangle([P(0.44, 0)[0], P(0, 0.80)[1], P(0.56, 0)[0], P(0, 0.92)[1]], fill=white)
        d.ellipse([P(0.50, 0)[0] - 3, P(0, 0.76)[1], P(0.50, 0)[0] + 3, P(0, 0.82)[1]], fill=GOLD)
    elif num == 8:
        # Shanghai at dusk: skyline with the Oriental Pearl Tower
        vgrad(d, x, y, w, int(h * 0.62), (24, 32, 72), (235, 150, 70))
        d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(18, 20, 34))
        # Oriental Pearl Tower: wide legs, BIG lower sphere, smaller
        # upper sphere, thin spire with a tiny top sphere
        tx = P(0.45, 0)[0]
        d.line([(tx - 8, P(0, 0.82)[1]), (tx - 3, P(0, 0.55)[1])], fill=(220, 220, 215), width=2)
        d.line([(tx + 8, P(0, 0.82)[1]), (tx + 3, P(0, 0.55)[1])], fill=(220, 220, 215), width=2)
        d.ellipse([tx - 7, P(0, 0.40)[1], tx + 7, P(0, 0.70)[1]], fill=(220, 90, 110))
        d.line([tx - 7, P(0, 0.55)[1], tx + 7, P(0, 0.55)[1]], fill=(240, 140, 160), width=1)
        d.ellipse([tx - 5, P(0, 0.42)[1], tx - 1, P(0, 0.47)[1]], fill=(245, 200, 210))
        d.ellipse([tx - 4, P(0, 0.18)[1], tx + 4, P(0, 0.36)[1]], fill=(220, 90, 110))
        d.ellipse([tx - 3, P(0, 0.19)[1], tx, P(0, 0.23)[1]], fill=(245, 200, 210))
        d.line([tx, P(0, 0.18)[1], tx, P(0, 0.02)[1]], fill=(220, 220, 215), width=2)
        d.ellipse([tx - 2, P(0, 0.02)[1], tx + 2, P(0, 0.08)[1]], fill=(200, 60, 50))
        for (bu0, bu1, btop) in [(0.24, 0.34, 0.55), (0.60, 0.70, 0.50),
                                 (0.80, 0.90, 0.58), (0.92, 0.99, 0.50)]:
            bx0, bx1 = P(bu0, 0)[0], P(bu1, 0)[0]
            by = P(0, btop)[1]
            d.rectangle([bx0, by, bx1, P(0, 0.80)[1]], fill=(16, 18, 32))
            for wx in range(int(bx0) + 3, int(bx1) - 2, 6):
                for wy in range(int(by) + 4, int(P(0, 0.80)[1]) - 3, 8):
                    if (wx * 5 + wy * 3) % 4 < 2:
                        d.rectangle([wx, wy, wx + 1, wy + 1], fill=(230, 190, 60))
        d.line([P(0.16, 0)[0], P(0, 0.42)[1], P(0.16, 0)[0], P(0, 0.10)[1]], fill=white, width=2)
        d.polygon([(P(0.16, 0)[0], P(0, 0.10)[1]), (P(0.16, 0)[0] + 12, P(0, 0.14)[1]),
                   (P(0.16, 0)[0], P(0, 0.18)[1])], fill=RED)
    elif num == 9:
        # Beirut street: a damaged building, fire at its base, smoke rising
        d.rectangle([x, y, x + w, y + h], fill=(150, 160, 180))
        d.rectangle([x, y + int(h * 0.78), x + w, y + h], fill=(90, 88, 84))
        for (bu0, bu1, btop) in [(0.02, 0.24, 0.30), (0.76, 0.98, 0.24)]:
            bx0, bx1 = P(bu0, 0)[0], P(bu1, 0)[0]
            by = P(0, btop)[1]
            d.rectangle([bx0, by, bx1, P(0, 0.78)[1]], fill=(110, 112, 118))
            for wx in range(int(bx0) + 4, int(bx1) - 3, 9):
                for wy in range(int(by) + 5, int(P(0, 0.78)[1]) - 4, 10):
                    if (wx + wy) % 3 == 0:
                        d.rectangle([wx, wy, wx + 3, wy + 4], fill=(70, 72, 78))
        dx0, dx1 = P(0.36, 0)[0], P(0.64, 0)[0]
        d.polygon([(dx0, P(0, 0.78)[1]), (dx0, P(0, 0.42)[1]), (dx0 + 8, P(0, 0.36)[1]),
                   (dx0 + 16, P(0, 0.46)[1]), (dx0 + 24, P(0, 0.38)[1]), (dx1, P(0, 0.44)[1]),
                   (dx1, P(0, 0.78)[1])], fill=(80, 78, 74))
        fx = (dx0 + dx1) / 2
        d.polygon([(fx - 12, P(0, 0.78)[1]), (fx - 6, P(0, 0.58)[1]), (fx, P(0, 0.70)[1]),
                   (fx + 6, P(0, 0.56)[1]), (fx + 12, P(0, 0.78)[1])], fill=(230, 140, 40))
        d.polygon([(fx - 6, P(0, 0.78)[1]), (fx - 2, P(0, 0.66)[1]), (fx + 2, P(0, 0.72)[1]),
                   (fx + 6, P(0, 0.78)[1])], fill=(240, 200, 60))
        for (su, sv, sr) in [(0.50, 0.28, 7), (0.46, 0.16, 9), (0.54, 0.08, 5)]:
            sx, sy = P(su, sv)
            d.ellipse([sx - sr, sy - sr // 2, sx + sr, sy + sr // 2], fill=(200, 200, 200))
    elif num == 10:
        # Strait of Hormuz: a tanker with barrels in the strait
        vgrad(d, x, y, w, int(h * 0.35), (196, 208, 226), (238, 226, 200))
        d.rectangle([x, y + int(h * 0.35), x + w, y + h], fill=(38, 90, 140))
        for (wu, wv, wl) in [(0.10, 0.45, 0.10), (0.30, 0.70, 0.12),
                             (0.60, 0.85, 0.10), (0.85, 0.50, 0.08)]:
            wx, wy = P(wu, wv)
            d.line([wx, wy, wx + wl * w, wy], fill=(120, 160, 210), width=1)
        hx0, hx1 = P(0.12, 0)[0], P(0.88, 0)[0]
        hy = P(0, 0.60)[1]
        d.polygon([(hx0, hy), (hx1 - 10, hy), (hx1, hy + 10), (hx0 + 6, hy + 10)],
                  fill=(60, 62, 68))
        d.rectangle([hx0, hy - 3, hx1 - 10, hy], fill=(150, 150, 145))
        for (cu, cc) in [(0.30, (200, 60, 50)), (0.40, (60, 100, 180)),
                         (0.50, (230, 190, 60)), (0.60, (90, 170, 100))]:
            cx = P(cu, 0)[0]
            d.rectangle([cx, P(0, 0.42)[1], cx + 12, P(0, 0.54)[1]], fill=cc,
                        outline=(255, 255, 255))
        d.rectangle([P(0.70, 0)[0], P(0, 0.50)[1], P(0.78, 0)[0], P(0, 0.65)[1]], fill=white)
        for (bu, with_dollar) in [(0.18, True), (0.24, False)]:
            bx = P(bu, 0)[0]
            by0, by1 = P(0, 0.46)[1], P(0, 0.60)[1]
            d.ellipse([bx, by0, bx + 10, by0 + 4], fill=(70, 130, 190))
            d.rectangle([bx, by0 + 2, bx + 10, by1], fill=(70, 130, 190))
            d.ellipse([bx, by1 - 4, bx + 10, by1], fill=(50, 100, 160))
            if with_dollar:
                d.text((bx + 2, by0 + 2), "$", font=font(SANS_B, 9), fill=white)
        d.line([P(0.02, 0)[0], P(0, 0.78)[1], P(0.10, 0)[0], P(0, 0.78)[1]],
               fill=(200, 220, 240), width=1)
        d.line([P(0.04, 0)[0], P(0, 0.86)[1], P(0.14, 0)[0], P(0, 0.86)[1]],
               fill=(200, 220, 240), width=1)
    elif num == 11:
        # Canberra: Parliament House on its hill, with a price tag
        d.rectangle([x, y, x + w, y + h], fill=sky)
        d.polygon([(x, y + h), (x, P(0, 0.70)[1]), (x + int(w * 0.25), P(0, 0.55)[1]),
                   (x + int(w * 0.50), P(0, 0.50)[1]), (x + int(w * 0.75), P(0, 0.55)[1]),
                   (x + w, P(0, 0.70)[1]), (x + w, y + h)], fill=(96, 160, 96))
        bx0, bx1 = P(0.30, 0)[0], P(0.68, 0)[0]
        by0, by1 = P(0, 0.42)[1], P(0, 0.62)[1]
        d.rectangle([bx0, by0, bx1, by1], fill=white)
        for cx in [0.36, 0.44, 0.52, 0.60]:
            d.rectangle([P(cx, 0)[0] - 2, by0 + 3, P(cx, 0)[0] + 2, by1], fill=(200, 200, 195))
        d.line([P(0.49, 0)[0], P(0, 0.42)[1], P(0.49, 0)[0], P(0, 0.08)[1]], fill=grey, width=2)
        d.rectangle([P(0.49, 0)[0], P(0, 0.08)[1], P(0.49, 0)[0] + 12, P(0, 0.14)[1]],
                    fill=(60, 100, 180))
        d.ellipse([P(0.49, 0)[0] + 4, P(0, 0.10)[1], P(0.49, 0)[0] + 8, P(0, 0.13)[1]],
                  fill=white)
        # price tag, big enough to read: pointed end left with a
        # punched hole, string looping up, "3.8%" printed on it
        tx0, tx1 = P(0.03, 0)[0], P(0.27, 0)[0]
        ty0, ty1 = P(0, 0.46)[1], P(0, 0.78)[1]
        midy = (ty0 + ty1) / 2
        d.polygon([(tx0 + 7, ty0), (tx1, ty0), (tx1, ty1), (tx0 + 7, ty1),
                   (tx0, midy)], fill=(230, 190, 60), outline=(180, 140, 40))
        d.ellipse([tx0 + 2, midy - 3, tx0 + 8, midy + 3], fill=NAVY)
        d.ellipse([tx0 + 4, midy - 1, tx0 + 6, midy + 1], fill=(255, 255, 255))
        d.line([tx0 + 5, midy, P(0.01, 0)[0], P(0, 0.36)[1]], fill=RED, width=1)
        d.text((tx0 + 12, midy - 5), "3.8%", font=font(SANS_B, 8), fill=NAVY)
    elif num == 12:
        # Geneva: a row of UN flags with the orange 16 Days ribbon
        d.rectangle([x, y, x + w, y + h], fill=CREAM)
        d.rectangle([x, y + int(h * 0.85), x + w, y + h], fill=(200, 196, 186))
        for pu in [0.14, 0.28, 0.42, 0.56, 0.70]:
            px = P(pu, 0)[0]
            d.line([px, P(0, 0.50)[1], px, P(0, 0.88)[1]], fill=grey, width=2)
            d.rectangle([px, P(0, 0.50)[1], px + 13, P(0, 0.62)[1]], fill=(60, 100, 180))
            d.ellipse([px + 4, P(0, 0.53)[1], px + 9, P(0, 0.59)[1]], fill=white)
        # 16 Days ribbon: folded loop at top, two tails crossing at
        # the loop's base and hanging down with notched ends
        rx0, rx1 = P(0.30, 0)[0], P(0.44, 0)[0]
        ry0, ry1 = P(0, 0.14)[1], P(0, 0.40)[1]
        d.ellipse([rx0, ry0, rx1, ry1], outline=(230, 120, 40), width=4)
        d.ellipse([rx0 + 4, ry0 + 4, rx1 - 4, ry1 - 4], fill=CREAM)
        cxm = (rx0 + rx1) / 2
        base_y = ry1 - 2
        d.polygon([(cxm - 6, base_y), (cxm + 1, base_y), (cxm - 2, P(0, 0.66)[1]),
                   (cxm - 5, P(0, 0.60)[1]), (cxm - 8, P(0, 0.66)[1])],
                  fill=(230, 120, 40))
        d.polygon([(cxm - 1, base_y), (cxm + 6, base_y), (cxm + 8, P(0, 0.62)[1]),
                   (cxm + 5, P(0, 0.56)[1]), (cxm + 2, P(0, 0.62)[1])],
                  fill=(230, 120, 40))
    elif num == 13:
        # New Delhi: a street rally under a tricolour banner, megaphone up
        d.rectangle([x, y, x + w, y + h], fill=(244, 238, 223))
        d.rectangle([x, y, x + w, P(0, 0.10)[1]], fill=(230, 140, 40))
        d.rectangle([x, P(0, 0.10)[1], x + w, P(0, 0.20)[1]], fill=white)
        d.rectangle([x, P(0, 0.20)[1], x + w, P(0, 0.30)[1]], fill=(40, 140, 70))
        skin = (210, 180, 140)
        caps = [(200, 60, 50), (60, 100, 180), (230, 140, 40), (40, 140, 70)]
        for i, cu in enumerate([0.06, 0.16, 0.26, 0.36, 0.46, 0.56, 0.66]):
            cx = P(cu, 0)[0]
            cy = P(0, 0.66)[1]
            d.rectangle([cx - 7, cy + 4, cx + 7, y + h], fill=caps[i % 4])
            d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=skin)
            d.ellipse([cx - 6, cy - 6, cx + 6, cy - 1], fill=caps[i % 4])
        # megaphone held up mid-rally, left of the status pill (the old
        # right-side position hid behind the pill)
        mx0, mx1 = P(0.30, 0)[0], P(0.48, 0)[0]
        my0, my1 = P(0, 0.36)[1], P(0, 0.52)[1]
        d.polygon([(mx0, (my0 + my1) / 2 - 4), (mx1, my0), (mx1, my1), (mx0, (my0 + my1) / 2 + 4)],
                  fill=white, outline=grey)
        d.rectangle([mx0 - 6, (my0 + my1) / 2 - 3, mx0, (my0 + my1) / 2 + 3], fill=(230, 190, 60))
        d.arc([mx1 + 2, my0 - 2, mx1 + 9, my1], -60, 60, fill=(230, 190, 60), width=2)
    elif num == 14:
        # Crimea at night: a pylon over a blacked-out city, two lights on
        d.rectangle([x, y, x + w, y + h], fill=(16, 18, 32))
        for (su, sv) in [(0.22, 0.12), (0.32, 0.08), (0.42, 0.16), (0.28, 0.22)]:
            sx, sy = P(su, sv)
            d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=white)
        for (bu0, bu1, btop) in [(0.02, 0.20, 0.55), (0.30, 0.48, 0.48), (0.52, 0.70, 0.58)]:
            bx0, bx1 = P(bu0, 0)[0], P(bu1, 0)[0]
            by = P(0, btop)[1]
            d.rectangle([bx0, by, bx1, y + h], fill=(10, 12, 24))
        d.rectangle([P(0.66, 0)[0] + 3, P(0, 0.56)[1], P(0.66, 0)[0] + 5, P(0, 0.58)[1]],
                    fill=(230, 190, 60))
        d.rectangle([P(0.44, 0)[0] + 3, P(0, 0.64)[1], P(0.44, 0)[0] + 5, P(0, 0.66)[1]],
                    fill=(230, 190, 60))
        tx = P(0.45, 0)[0]
        d.line([(tx - 8, y + h), (tx, P(0, 0.15)[1])], fill=(140, 140, 150), width=2)
        d.line([(tx + 8, y + h), (tx, P(0, 0.15)[1])], fill=(140, 140, 150), width=2)
        d.line([tx - 16, P(0, 0.30)[1], tx + 16, P(0, 0.30)[1]], fill=(140, 140, 150), width=2)
        d.line([tx - 10, P(0, 0.45)[1], tx + 10, P(0, 0.45)[1]], fill=(140, 140, 150), width=2)
        d.line([tx - 12, P(0, 0.62)[1], tx + 12, P(0, 0.62)[1]], fill=(140, 140, 150), width=2)
        d.ellipse([tx - 2, P(0, 0.12)[1], tx + 2, P(0, 0.16)[1]], fill=(230, 190, 60))
        d.line([P(0.10, 0)[0], P(0, 0.20)[1], tx, P(0, 0.15)[1]], fill=(140, 140, 150), width=1)
    elif num == 15:
        # Bangkok: parliament with its golden spire, leaf and check
        d.rectangle([x, y, x + w, y + h], fill=sky)
        d.rectangle([x, P(0, 0.75)[1], x + w, y + h], fill=(96, 160, 96))
        bx0, bx1 = P(0.20, 0)[0], P(0.58, 0)[0]
        by0, by1 = P(0, 0.40)[1], P(0, 0.75)[1]
        d.polygon([(bx0, by0), (bx1, by0), ((bx0 + bx1) / 2, P(0, 0.22)[1])], fill=GOLD)
        d.rectangle([bx0, by0, bx1, by1], fill=white)
        for cx in [0.26, 0.34, 0.42, 0.50]:
            d.rectangle([P(cx, 0)[0] - 2, by0 + 3, P(cx, 0)[0] + 2, by1], fill=(200, 200, 195))
        sx = P(0.39, 0)[0]
        d.line([sx, P(0, 0.22)[1], sx, P(0, 0.06)[1]], fill=GOLD, width=2)
        d.ellipse([sx - 3, P(0, 0.03)[1], sx + 3, P(0, 0.09)[1]], fill=GOLD)
        lx0, lx1 = P(0.60, 0)[0], P(0.75, 0)[0]
        ly0, ly1 = P(0, 0.55)[1], P(0, 0.85)[1]
        d.polygon([(lx0, (ly0 + ly1) / 2), ((lx0 + lx1) / 2, ly0), (lx1, (ly0 + ly1) / 2),
                   ((lx0 + lx1) / 2, ly1)], fill=(60, 160, 80))
        d.line([(lx0, ly1), ((lx0 + lx1) / 2, (ly0 + ly1) / 2)], fill=(40, 120, 60), width=1)
        d.line([(lx0 + 3, ly1 - 6), (lx0 + 7, ly1 - 2), (lx0 + 14, ly1 - 12)], fill=white, width=2)


def draw_status_pill(d, text, x, y):
    f = font(SANS_B, 10)
    tw = f.getlength(text)
    pad = 6
    d.rounded_rectangle([x, y, x + tw + pad * 2, y + 16], radius=3, fill=STATUS_COLORS[text])
    d.text((x + pad, y + 3), text, font=f, fill=(255, 255, 255))


def draw_panel(p, x, y, w, h, large):
    img = Image.new("RGB", (w, h), PANEL_BG)
    d = ImageDraw.Draw(img)
    band_h = 96 if large else 44
    d.rectangle([0, 0, w, band_h], fill=NAVY)
    # hero panels get a schematic mini-map; small panels get a drawn
    # mini-scene of the story's event. The status pill sits top-right
    # of the band and the number badge top-left; a small number accent
    # (if any) sits on a navy chip in the bottom-right corner, so the
    # scene fills the band and reads as a picture, like the 22 Nov
    # winner — the number is an accent, not the picture.
    if large and p[13]:
        draw_mini_map(d, p[13], 6, 2, w - 12, band_h - 4)
    elif not large:
        draw_small_scene(d, p[0], 6, 2, w - 12, band_h - 4)
        if p[14]:
            nf2_size = 12
            nf2 = font(SANS_B, nf2_size)
            while nf2.getlength(p[14]) > 60 and nf2_size > 9:
                nf2_size -= 1
                nf2 = font(SANS_B, nf2_size)
            nw2 = nf2.getlength(p[14])
            chip_x = w - 6 - nw2 - 10
            chip_y0 = band_h - 18
            d.rounded_rectangle([chip_x, chip_y0, chip_x + nw2 + 10, band_h - 2],
                                radius=3, fill=NAVY)
            d.text((chip_x + 5, chip_y0 + 2), p[14], font=nf2, fill=GOLD)
    # number badge top left
    nf = font(SANS_B, 13 if large else 11)
    num = str(p[0])
    nw = nf.getlength(num) + 10
    d.ellipse([4, 4, 4 + nw, 4 + 18], fill=RED)
    d.text((4 + 5, 6), num, font=nf, fill=(255, 255, 255))
    draw_status_pill(d, p[7], w - font(SANS_B, 10).getlength(p[7]) - 16, 5)
    # region + topic
    ty = band_h + 6
    rf = font(SANS_B, 11 if large else 10)
    d.text((6, ty), p[1] + " - " + p[2], font=rf, fill=REGION_COLORS[p[1]])
    ty += 15 if large else 14
    pf = font(SANS_B, 11 if large else 10)
    # country flag chip before the place label
    fw, fh = (18, 12) if large else (14, 10)
    draw_flag(d, PANEL_FLAGS[p[0] - 1], 6, ty + 1, fw, fh)
    d.text((6 + fw + (4 if large else 3), ty), p[3], font=pf, fill=INK)
    ty += 15 if large else 14
    # headline
    hf_size = 17 if large else 13
    hf = font(SERIF_B, hf_size)
    while hf.getlength(p[4]) > (w - 12) * 2 and hf_size > 11:
        hf_size -= 1
        hf = font(SERIF_B, hf_size)
    lines = fit_lines(p[4], hf, w - 12, 2)
    for ln in lines:
        d.text((6, ty), ln, font=hf, fill=INK)
        ty += hf_size + 3
    # deck
    df = font(SANS, 11 if large else 10)
    max_deck = 3 if large else 2
    dlines = fit_lines(p[5], df, w - 12, max_deck)
    for ln in dlines:
        d.text((6, ty), ln, font=df, fill=(50, 48, 44))
        ty += 14 if large else 13
    # source at bottom
    sf = font(SANS, 9 if large else 8)
    d.text((6, h - 14), p[6], font=sf, fill=GREY)
    # border: 2px, same weight and colour on every panel on the page
    d.rectangle([0, 0, w - 1, h - 1], outline=BORDER, width=2)
    return img

def draw_numbers(x, y, w, h):
    img = Image.new("RGB", (w, h), NAVY)
    d = ImageDraw.Draw(img)
    tf = font(SANS_B, 13)
    d.text((10, 8), "THE DAY IN NUMBERS", font=tf, fill=(255, 255, 255))
    d.line([10, 28, w - 10, 28], fill=GOLD, width=2)
    nf = font(SANS_B, 21)
    cf = font(SANS, 10)
    yy = 38
    for num, cap in NUMBERS:
        d.text((10, yy), num, font=nf, fill=GOLD)
        nw = nf.getlength(num)
        # caption wrapped to the right of the number
        cap_lines = wrap(cap, cf, w - 20 - nw - 8)
        cy = yy + 4
        for ln in cap_lines[:2]:
            d.text((10 + nw + 8, cy), ln, font=cf, fill=(235, 235, 230))
            cy += 12
        yy += 26
    d.rectangle([0, 0, w - 1, h - 1], outline=BORDER, width=2)
    return img


# world map, 56 cols x 19 rows (lon -170..190, lat 78..-56), redrawn so each
# continent reads as one shape: the Americas taper south instead of a stray
# full-height bar, Africa narrows south, Australia sits apart from SE Asia
MAP_ROWS = [
    "#####            #####           ######################",
    "#######################          ######################",
    "##################     #  #####  ######################",
    "   ##############        ####### ######################",
    "    #############        ####### #####################",
    "       ##########        ######   ###################",
    "        ########         ### #######################",
    "        ######           ########################",
    "          ####          ########################",
    "              #######   ###########  ######",
    "              #######   ###########   #  ##",
    "              ######        ######       #######",
    "              #####         ######        ########",
    "               ####         #####           ######",
    "               ###          #####           ######",
    "               ###           ###             #####",
    "               ##            ###             ####    #",
    "               ##                                    #",
    "               ##",
]
MAP_COLS = 56
MAP_TOP_LAT, MAP_BOT_LAT = 78.0, -56.0


def draw_map_panel(x, y, w, h):
    img = Image.new("RGB", (w, h), PANEL_BG)
    d = ImageDraw.Draw(img)
    mx, my = 8, 26
    mw, mh = w - 16, h - 46
    dx = mw / MAP_COLS
    dy = mh / len(MAP_ROWS)
    # solid landmass blocks (one filled cell per "#" in the coarse grid),
    # drawn at 3x and downscaled so the coastlines anti-alias instead
    # of stair-stepping at 2x zoom
    S = 3
    land = Image.new("RGB", (w * S, h * S), PANEL_BG)
    ld = ImageDraw.Draw(land)
    for r, row in enumerate(MAP_ROWS):
        for c, ch in enumerate(row):
            if ch == "#":
                px = (mx + c * dx) * S
                py = (my + r * dy) * S
                ld.rectangle([px, py, px + dx * S + 0.5, py + dy * S + 0.5],
                             fill=(120, 140, 170))
    img.paste(land.resize((w, h), Image.LANCZOS), (0, 0))
    tf = font(SANS_B, 12)
    d.text((8, 6), "WHERE IT HAPPENED", font=tf, fill=INK)
    sf = font(SANS, 9)
    d.text((w - 118, 8), "pins = story numbers", font=sf, fill=GREY)
    # pins coloured by each story's region, same colours as the panel tags
    pf = font(SANS_B, 9)
    for p in PANELS:
        lon, lat = p[10], p[9]
        col = (lon + 170.0) / 360.0 * MAP_COLS
        row = (MAP_TOP_LAT - lat) / (MAP_TOP_LAT - MAP_BOT_LAT) * len(MAP_ROWS)
        px = mx + col * dx + p[11]
        py = my + row * dy + p[12]
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=(255, 255, 255))
        d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=REGION_COLORS[p[1]], outline=(255, 255, 255), width=1)
        num = str(p[0])
        tw = pf.getlength(num)
        d.text((px - tw / 2, py - 5), num, font=pf, fill=(255, 255, 255))
    # region legend: colour dot + code per region, centred under the map
    lgf = font(SANS_B, 8)
    codes = [("EU", "EUROPE"), ("ME", "MIDDLE EAST"), ("AF", "AFRICA"),
             ("SA", "SOUTH ASIA"), ("EA", "EAST ASIA"), ("SEA", "SE ASIA"),
             ("AM", "AMERICAS"), ("OC", "OCEANIA"), ("WO", "WORLD")]
    total = sum(7 + 2 + lgf.getlength(c) + 8 for c, _ in codes) - 8
    lx = (w - total) / 2
    ly = h - 15
    for code, name in codes:
        d.ellipse([lx, ly + 1, lx + 6, ly + 7], fill=REGION_COLORS[name])
        d.text((lx + 8, ly), code, font=lgf, fill=GREY)
        lx += 7 + 2 + lgf.getlength(code) + 8
    d.rectangle([0, 0, w - 1, h - 1], outline=BORDER, width=2)
    return img


def build():
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    M = 8
    CW = W - 2 * M
    # top navy bar
    d.rectangle([0, 0, W, 22], fill=NAVY)
    bf = font(SANS_B, 12)
    d.text((M, 4), "THE WORLD IN ONE DAY", font=bf, fill=(255, 255, 255))
    day = "  -  DAY 329 OF 2026"
    d.text((M + bf.getlength("THE WORLD IN ONE DAY"), 4), day, font=bf, fill=GOLD)
    rt = "37 STORIES - 9 REGIONS - EDITION TO 13:30 UTC"
    d.text((W - M - bf.getlength(rt), 4), rt, font=bf, fill=GOLD)
    # masthead: title at 50pt (was 56) so its "y" descender (ink bottom
    # y=80) clears the red sub-headline below (ink top y=84, 4px gap);
    # at 56pt the descender reached y=87 while the sub-headline ink
    # started at y=78 -- a 9px overlap the user spotted
    mf = font(SERIF_B, 50)
    title = "Wednesday 25 November 2026"
    while mf.getlength(title) > CW:
        mf = font(SERIF_B, mf.size - 2)
    d.text((M, 22), title, font=mf, fill=INK)
    # red sub-headline strip
    rf = font(SERIF, 16)
    sub = "Shenzhou-24 carries first foreign astronaut to Tiangong  -  US readies tariffs on 16 economies  -  Asian stocks tumble"
    while rf.getlength(sub) > CW:
        rf = font(SERIF, rf.size - 1)
    d.text((M, 82), sub, font=rf, fill=RED)
    # divider under the masthead, same 2px weight as every panel border
    d.line([M, 103, W - M, 103], fill=BORDER, width=2)
    # region bars (equal width so every label fits)
    bx, by = M, 106
    bh = 18
    bw = CW // len(REGION_COUNTS)
    for name, cnt in REGION_COUNTS:
        d.rectangle([bx, by, bx + bw - 1, by + bh], fill=REGION_COLORS[name])
        lf = font(SANS_B, 10)
        label = name + " " + str(cnt)
        d.text((bx + 4, by + 5), label, font=lf, fill=(255, 255, 255))
        bx += bw
    # frame the whole region strip in the same 2px border, with 1px
    # dividers between regions so each sector reads as its own cell
    d.rectangle([M, by, W - M, by + bh], outline=BORDER, width=2)
    for i in range(1, len(REGION_COUNTS)):
        dxv = M + i * bw
        d.line([dxv, by + 2, dxv, by + bh - 2], fill=BORDER, width=1)
    # timeline strip: a TRUE proportional time axis, 00:00-18:00 UTC.
    # Dots sit at their real times. The 00:18-00:30 cluster is tight,
    # so its two times share ONE label ("00:18-00:30") centred on the
    # cluster, and its two events share ONE joined label below the
    # line — so every event label on the strip sits on ONE baseline.
    # Hour ticks with hour numbers sit below the line. Hollow dots =
    # scheduled.
    ty = 125
    th = 89
    # gold 2px frame: same weight as every other border, gold so it reads
    # on the dark strip (the strip's own palette colour)
    d.rectangle([M, ty, W - M, ty + th], fill=(20, 20, 20), outline=GOLD, width=2)
    tf = font(SANS_B, 11)
    d.text((M + 6, ty + 14), "THE DAY IN UTC", font=tf, fill=GOLD)
    ax0 = M + 118
    ax1 = W - M - 8

    def tmins(t):
        return int(t[:2]) * 60 + int(t[3:])

    def dot_x(t):
        return ax0 + (ax1 - ax0) * tmins(t) / 1080.0

    ay_line = ty + 34
    d.line([ax0, ay_line, ax1, ay_line], fill=(120, 116, 108), width=2)
    # hour ticks + hour numbers
    hf = font(SANS_B, 8)
    for hh in range(0, 19, 3):
        hx = ax0 + int((ax1 - ax0) * hh / 18)
        d.line([hx, ay_line - 4, hx, ay_line + 4], fill=(150, 146, 138), width=1)
        lab = "%02d:00" % hh
        lw = hf.getlength(lab)
        d.text((min(max(hx - lw / 2, ax0), ax1 - lw), ay_line + 3), lab, font=hf,
               fill=(150, 146, 138))
    # greedy tier assignment: a label joins the first tier where it
    # clears the previous label in that tier (times need 32px, events
    # need their own half-widths plus 4px)
    tf2 = font(SANS_B, 10)
    ef = font(SANS, 10)
    t_last = [-10 ** 9] * 3
    e_last = [(-10 ** 9, 0.0)] * 4
    # one merged time label for the 00:18-00:30 cluster, centred on it;
    # tier 0 is taken up to the merged label's right edge
    clab = "00:18-00:30"
    clw = tf2.getlength(clab)
    ccx = (dot_x("00:18") + dot_x("00:30")) / 2
    ctx = min(max(ccx - clw / 2, ax0), ax1 - clw)
    d.text((ctx, ty + 22), clab, font=tf2, fill=GOLD)
    t_last[0] = ctx + clw
    for i, (t, ev) in enumerate(TIMELINE):
        cx = dot_x(t)
        if i >= 2:  # every entry outside the 2-item cluster gets its own time label
            tier = 2
            for j in range(3):
                if cx - t_last[j] >= 32:
                    tier = j
                    break
            t_last[tier] = cx
            tw = tf2.getlength(t)
            tx = min(max(cx - tw / 2, M), ax1 - tw)
            d.text((tx, ty + 22 - tier * 10), t, font=tf2, fill=GOLD)
        hw = ef.getlength(ev) / 2 + 3
        if i == 0:
            # cluster: both events joined on the ONE shared event
            # baseline (ty + 44), centred on the cluster midpoint.
            # Stacking was rejected: the upper line would have to sit
            # on the axis line / hour numbers (measured). The joined
            # line spans ~51..240, clearing "Crimea cuts begin"
            # (~325..417) by ~85px.
            joined = "Shenzhou lifts off · Australia CPI 3.8%"
            jw = ef.getlength(joined)
            ccx = (dot_x("00:18") + dot_x("00:30")) / 2
            jx = min(max(ccx - jw / 2, M), ax1 - jw)
            d.text((jx, ty + 44), joined, font=ef, fill=(235, 235, 230))
            e_last[0] = (ccx, jw / 2 + 3)
        elif i == 1:
            pass  # event already in the joined cluster label above
        else:
            etier = 3
            for k in range(4):
                lx, lhw = e_last[k]
                if cx - hw >= lx + lhw + 4:
                    etier = k
                    break
            e_last[etier] = (cx, hw)
            ex = min(max(cx - hw + 3, M), ax1 - 2 * hw + 6)
            d.text((ex, ty + 44 + etier * 10), ev, font=ef, fill=(235, 235, 230))
        sched = "(sched.)" in ev
        if sched:
            d.ellipse([cx - 3, ay_line - 3, cx + 3, ay_line + 3], outline=GOLD, width=2)
        else:
            d.ellipse([cx - 3, ay_line - 3, cx + 3, ay_line + 3], fill=GOLD)
    # panels row 1: 3 large + numbers
    py1, ph1 = 216, 232
    col_w = (CW - 3 * 6) // 4
    for i, p in enumerate(PANELS[:3]):
        px = M + i * (col_w + 6)
        img.paste(draw_panel(p, px, py1, col_w, ph1, True), (px, py1))
    nx = M + 3 * (col_w + 6)
    img.paste(draw_numbers(nx, py1, col_w, ph1), (nx, py1))
    # rows 2 and 3: 6 small each
    sw = (CW - 5 * 6) // 6
    for row, y0 in enumerate((454, 612)):
        for i in range(6):
            p = PANELS[3 + row * 6 + i]
            px = M + i * (sw + 6)
            img.paste(draw_panel(p, px, y0, sw, 152, False), (px, y0))
    # ALSO TODAY + map
    ay = 770
    ah = 160
    aw = 622
    mw = CW - aw - 6
    d.rectangle([M, ay, M + aw, ay + ah], fill=PANEL_BG, outline=BORDER, width=2)
    hf = font(SANS_B, 13)
    d.text((M + 8, ay + 6), "ALSO TODAY", font=hf, fill=INK)
    sub2 = "- 22 more stories from Wednesday 25 November"
    d.text((M + 8 + hf.getlength("ALSO TODAY") + 6, ay + 8), sub2, font=font(SANS, 11), fill=GREY)
    # two columns of 11; numbers coloured by each item's region
    itf = font(SANS, 10)
    btf = font(SANS_B, 10)
    stf = font(SANS, 9)
    col_w2 = (aw - 16) // 2
    for ci in range(2):
        cx = M + 8 + ci * col_w2
        for ri in range(11):
            idx = ci * 11 + ri
            num, text, src = ALSO[idx]
            yy = ay + 23 + ri * 12
            d.text((cx, yy), str(num), font=btf, fill=REGION_COLORS[ALSO_REGIONS[idx]])
            nw = btf.getlength(str(num)) + 4
            # shorten text to fit (measured with the fonts actually drawn:
            # #25's source is bold so "Bernama" stays legible at 9px,
            # #33's source is 8px so the full place name fits; the second
            # column runs 8px further right, to the panel edge)
            sfont = font(SANS_B, 9) if num == 25 else (font(SANS, 8) if num == 33 else stf)
            room = col_w2 - nw - 4 + (8 if ci == 1 else 0)
            t = text
            while itf.getlength(t) + sfont.getlength(" - " + src) > room and len(t) > 10:
                t = t.rsplit(" ", 1)[0]
            d.text((cx + nw, yy), t, font=itf, fill=INK)
            d.text((cx + nw + itf.getlength(t), yy), " - " + src, font=sfont, fill=GREY)
    img.paste(draw_map_panel(M + aw + 6, ay, mw, ah), (M + aw + 6, ay))
    # date check footer
    fy = 936
    fh = 58
    # divider above the footer, same 2px weight as every panel border
    d.line([M, 932, W - M, 932], fill=BORDER, width=2)
    d.rectangle([M, fy, W - M, fy + fh], fill=(255, 255, 255), outline=BORDER, width=2)
    d.rectangle([M, fy, M + 96, fy + fh], fill=RED)
    df = font(SANS_B, 12)
    d.text((M + 10, fy + 8), "DATE CHECK", font=df, fill=(255, 255, 255))
    d.text((M + 10, fy + 28), "25 NOV ONLY", font=font(SANS_B, 10), fill=(255, 255, 255))
    tf2 = font(SANS_B, 11)
    d.text((M + 104, fy + 5), "Every story here happened, or was first reported, on Wednesday 25 November 2026 (UTC).",
           font=tf2, fill=INK)
    lf2 = font(SANS, 10)
    lines = fit_lines(LEFT_OUT, lf2, CW - 104 - 8, 2)
    yy = fy + 18
    for ln in lines:
        d.text((M + 104, yy), ln, font=lf2, fill=(60, 58, 52))
        yy += 12
    # nuance notes: one launch-time fact and what was not yet known
    nf = font(SANS, 10)
    notes = ("Notes: Shenzhou-24 launched 00:18 UTC 25 Nov (08:18 Beijing) - "
             "Not yet when drawn: US inflation/GDP 13:30 UTC")
    d.text((M + 104, fy + fh - 17), notes, font=nf, fill=(60, 58, 52))
    # legend line
    ly = 996
    legend = ("HOW SURE: CONFIRMED = two or more outlets - OFFICIAL = on the record - "
              "REPORTED = carried by the day's wires - CLAIM = one side's account - "
              "ONGOING = still unfolding - Scenes are drawn, not photos.")
    lf3 = font(SANS, 9)
    while lf3.getlength(legend) > CW:
        legend = legend.rsplit(" - ", 1)[0] + "."
    d.text((M, ly), legend, font=lf3, fill=GREY)
    # bottom line
    by = 1008
    bf2 = font(SANS_B, 10)
    bl = "25 NOVEMBER 2026  -  THE DAY'S WORLD NEWS, IN ONE IMAGE"
    d.text(((W - bf2.getlength(bl)) // 2, by), bl, font=bf2, fill=GREY)
    return img


if __name__ == "__main__":
    out = build()
    out.save("entry.png", optimize=True)
    print("saved entry.png", out.size)
