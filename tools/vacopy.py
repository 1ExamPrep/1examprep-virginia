"""Copy for passyourvirginiacontractorexam.com: what each license covers and the facts per license group.

Edit freely, then run python3 build.py. Figures here were checked against the DPOR and DHCD pages
listed in SOURCES on 2026-10-19. Re-check them when the boards change their rules.
"""

DPOR_CONTRACTORS = "https://www.dpor.virginia.gov/Boards/Contractors"
DPOR_TRADESMEN = "https://www.dpor.virginia.gov/Boards/Tradesmen/"
DHCD_CERT = "https://www.dhcd.virginia.gov/earn-certification"
PSI_BULLETIN = "https://www.dpor.virginia.gov/sites/default/files/boards/Contractors/CIB_PSI_Contr_BusDE.pdf"
VA_CODE_1100 = "https://law.lis.virginia.gov/vacode/title54.1/chapter11/section54.1-1100/"

SOURCES = {
    "contractor": [("Virginia Board for Contractors (DPOR)", DPOR_CONTRACTORS), ("Code of Virginia, section 54.1-1100: license classes", VA_CODE_1100), ("PSI candidate bulletin for the Virginia contractor exams", PSI_BULLETIN)],
    "business": [("Virginia Board for Contractors (DPOR)", DPOR_CONTRACTORS), ("PSI candidate bulletin for the Virginia contractor exams", PSI_BULLETIN), ("Code of Virginia, section 54.1-1100: license classes", VA_CODE_1100)],
    "trades": [("DPOR Tradesmen program, Board for Contractors", DPOR_TRADESMEN), ("Virginia Board for Contractors (DPOR)", DPOR_CONTRACTORS)],
    "officials": [("DHCD: earn a code official certification", DHCD_CERT), ("Virginia Board for Contractors (DPOR)", DPOR_CONTRACTORS)],
    "codes": [("Virginia Board for Contractors (DPOR)", DPOR_CONTRACTORS), ("DHCD: earn a code official certification", DHCD_CERT)],
}

# One or two plain sentences on the work each classification covers. Written as "work such as" because
# the board's regulation has the legal definition; the class page links to it.
SCOPE = {
    "commercial-building": "The Commercial Building Contractor (CBC) classification covers construction, remodeling and repair of commercial buildings and structures of any size, along with the site work that goes with them.",
    "commercial-improvement": "The Commercial Improvement Contractor (CIC) classification covers remodeling, repair and improvement work on existing commercial buildings, without new commercial construction.",
    "residential-building": "The Residential Building Contractor (RBC) classification covers building, remodeling and repairing one- and two-family homes and townhouses, plus the accessory structures on a residential lot.",
    "home-improvement": "The Home Improvement Contractor (HIC) classification covers remodeling, repair and improvement of existing residential buildings, such as kitchens, baths, decks, windows and siding.",
    "concrete": "The Concrete Contractor specialty covers concrete work such as footings, foundations, slabs, flatwork, curbs, sidewalks and driveways, including forms and reinforcing.",
    "masonry": "The Masonry Contractor specialty covers brick, block and stone work, including chimneys, fireplaces, veneer and masonry walls.",
    "roofing": "The Roofing Contractor specialty covers installing, repairing and replacing roof coverings, flashing, underlayment and roof drainage on any type of building.",
    "flooring": "The Floor and Floor Covering Contractor specialty covers installing wood, laminate, resilient and carpet flooring and the underlayment beneath it.",
    "painting": "The Painting and Wall Covering Contractor specialty covers interior and exterior painting, coatings, wallpaper and other wall coverings.",
    "tile": "The Tile, Marble, Ceramic and Terrazzo Contractor specialty covers setting tile, stone, marble and terrazzo on floors, walls and countertops.",
    "swimming-pool": "The Swimming Pool Construction Contractor specialty covers building, renovating and repairing in-ground and above-ground pools and spas, including their structural shell and finishes.",
    "refrigeration": "The Refrigeration Contractor specialty covers installing and servicing commercial and industrial refrigeration systems such as walk-in coolers, freezers and process cooling.",
    "fire-alarm": "The Fire Alarm Systems Contractor specialty covers installing, servicing and inspecting fire alarm and detection systems.",
    "framing": "The Framing Contractor specialty covers wood and light-gauge metal framing of floors, walls and roofs.",
    "finish-carpentry": "The Finish Carpentry Contractor specialty covers trim, millwork, cabinets, doors, stairs and other finish woodwork.",
    "insulation": "The Insulation and Weather Stripping Contractor specialty covers thermal and acoustic insulation, air sealing and weather stripping.",
    "marine-facility": "The Marine Facility Contractor specialty covers piers, docks, bulkheads, boat ramps and similar waterfront structures.",
    "alternative-energy": "The Alternative Energy Systems Contractor specialty covers solar, wind and other alternative energy installations, apart from the electrical connections a licensed electrical contractor makes.",
    "asphalt-paving": "The Asphalt Paving and Sealcoating Contractor specialty covers asphalt paving, patching, sealcoating and striping.",
    "billboard-sign": "The Billboard Sign Contractor specialty covers erecting, maintaining and removing outdoor advertising signs and their supports.",
    "farm-improvement": "The Farm Improvement Contractor specialty covers agricultural buildings and improvements such as barns, silos, fencing and other farm structures.",
    "landscape-irrigation": "The Landscape Irrigation Contractor specialty covers installing and servicing lawn and landscape irrigation systems.",
    "landscape-service": "The Landscape Service Contractor specialty covers landscape construction such as grading, hardscape, walkways and planting.",
    "steel-erection": "The Steel Erection Contractor specialty covers erecting structural steel, joists, decking and miscellaneous metals.",
    "underground-utility": "The Underground Utility and Excavating Contractor specialty covers trenching, excavation and installing underground utility lines.",
    "vessel": "The Vessel Contractor specialty covers construction and repair of tanks and pressure vessels.",
    "recreational-facility": "The Recreational Facility Contractor specialty covers athletic courts, tracks, playgrounds and similar recreational surfaces.",
    "nascla-commercial-general-building": "The NASCLA Commercial General Building exam is a national technical exam accepted by Virginia and several other states for commercial building work, so one pass can count in more than one state.",
    "business-and-law": "The business and law portion is the Virginia and general business exam for Class A and Class B licenses, written to the NASCLA Contractors Guide to Business, Law and Project Management, Virginia edition.",
    "pre-license-education": "The 8-hour pre-license course is required of every Class A, B and C applicant before the Board for Contractors will issue the license.",
    "licensing-services": "Licensing services help with the paperwork side: the Board for Contractors application and the company filing with the State Corporation Commission.",
    "journeyman-electrician": "The journeyman electrician license lets you do electrical work in Virginia under the supervision rules for tradesmen; the exam is written to the National Electrical Code edition Virginia has adopted.",
    "master-electrician": "The master electrician license is the top Virginia electrical tradesman license and can serve as the master for an electrical contracting firm.",
    "electrical-contractor-nascla": "The NASCLA electrical contractor exams are national technical exams for electrical contractors, accepted by a number of states that recognise NASCLA.",
    "journeyman-plumber": "The journeyman plumber license covers plumbing work under the Virginia tradesman rules; the exam is written to the plumbing code Virginia has adopted.",
    "master-plumber": "The master plumber license is the top Virginia plumbing tradesman license and can serve as the master for a plumbing contracting firm.",
    "residential-plumber": "The residential plumbing license, available since April 1, 2025, is limited to residential plumbing and needs less experience than the journeyman license.",
    "journeyman-hvac": "The journeyman HVAC license covers heating, ventilation and air conditioning work under the Virginia tradesman rules.",
    "master-hvac": "The master HVAC license is the top Virginia HVAC tradesman license and can serve as the master for an HVAC contracting firm.",
    "residential-hvac": "The residential HVAC mechanic license, available since April 1, 2025, is limited to residential HVAC work and needs less experience than the journeyman license.",
    "journeyman-gas-fitter": "The journeyman gas fitter license covers liquefied petroleum (LP) gas piping and appliance work under the Virginia tradesman rules.",
    "master-gas-fitter": "The master gas fitter license is the top Virginia LP gas fitting tradesman license.",
    "journeyman-natural-gas-fitter": "The journeyman natural gas fitter license covers natural gas piping and appliance connections under the Virginia tradesman rules.",
    "master-natural-gas-fitter": "The master natural gas fitter license is the top Virginia natural gas fitting tradesman license.",
    "code-books-and-courses": "Code books and short code courses cover the Virginia Uniform Statewide Building Code, the International Building and Plumbing Codes and OSHA construction rules.",
    "other": "Other exam prep collects products that do not fit a single license class.",
}
OFFICIAL_SCOPE = "The {name} certification is an ICC exam that Virginia code officials take as part of their DHCD certification, together with the Virginia Building Code Academy classes."

# facts per group, used in the "How the exam works" section and the FAQ
GROUP_FACTS = {
    "contractor": [
        "Virginia issues contractor licenses in three classes. Class C covers single jobs of $1,000 to under $10,000 and under $150,000 a year; Class B covers single jobs of $10,000 to under $120,000 and under $750,000 a year; Class A has no upper limit.",
        "Every applicant completes 8 hours of pre-license education before the license is issued.",
        "Class A and B firms name a designated employee or member of responsible management who passes the exams. PSI runs them, and the fee is $40 for one portion, $72 for two and $85 for three.",
        "The exams are open book. You bring your own references, which may be highlighted and permanently tabbed; removable flags and loose notes are not allowed.",
    ],
    "business": [
        "Class A and B applicants pass the Virginia and general business portions, written to the NASCLA Contractors Guide to Business, Law and Project Management, Virginia edition.",
        "Every Class A, B and C applicant completes 8 hours of pre-license education.",
        "PSI runs the exams; the fee is $40 for one portion, $72 for two and $85 for three.",
        "The exams are open book, with highlighting and permanent tabs allowed in your own references.",
    ],
    "trades": [
        "Tradesman licenses are issued by the Board for Contractors through its Tradesmen program, for electrical, plumbing, HVAC and gas fitting.",
        "The board has to approve you before PSI lets you schedule. The exam fee is $100 for journeyman and $125 for master.",
        "Pre-license education is required, and renewals need 3 hours of continuing education for electrical, plumbing and HVAC and 1 hour for gas fitting.",
        "Residential plumbing and residential HVAC mechanic licenses, added on April 1, 2025, need less experience than a journeyman license.",
    ],
    "officials": [
        "Virginia code officials are certified by the Department of Housing and Community Development (DHCD), not by DPOR.",
        "The path is the Virginia Building Code Academy Core class, the classes for your certification, then the required exam, usually an ICC exam.",
        "Building, fire and property maintenance officials apply within 12 months of hire; technical assistants have 18 months.",
        "Certified officials complete 16 hours of DHCD-approved continuing education every 2 years.",
    ],
    "codes": [
        "Contractor and tradesman exams in Virginia are open book, so the code books you bring decide how fast you find answers.",
        "Highlighting and permanent tabs are allowed in your own references; removable flags are not.",
        "Bring the edition named in your candidate bulletin, which is not always the newest one.",
        "Books ship from the fulfillment center; online courses arrive by email after purchase.",
    ],
}
GROUP_HOW = {
    "contractor": "The {name} exam is the technical portion of the license for that classification. A Class A or B firm usually also needs the business and law portion, and every applicant needs the 8-hour pre-license course.",
    "business": "The {name} products cover the business side of a Virginia contractor license, which every Class A and B firm deals with no matter which trade classification it holds.",
    "trades": "The {name} exam is a tradesman exam: one person is licensed, and a contracting firm in that trade also needs its own Board for Contractors license.",
    "officials": "The {name} exam is a code official certification. It is taken after the Virginia Building Code Academy Core class and leads to DHCD certification.",
    "codes": "The {name} items are references and short courses that sit beside the exam prep for any of the licenses on this site.",
}

# what each package type is, in one line
TYPE_BLURB = {
    "online-practice-exams": "timed practice questions online, with explanations",
    "online-course": "an online course with practice exams you can take on a phone or laptop",
    "tabs": "pre-printed permanent tabs for the reference books, allowed in the exam room",
    "study-guide-online-course": "the study guide plus the online course",
    "study-guide-flash-cards": "the study guide with practice exams plus flash cards",
    "study-guide": "the printed study guide with practice exams",
    "code-book": "the printed code book",
    "book-package": "the reference books the exam is written to, new and unmarked",
    "study-guide-nec-tabs": "the study guide, the National Electrical Code and pre-printed tabs",
    "study-guide-calculations-nec": "the study guide, the calculations guide and the National Electrical Code",
    "super-combo": "study guide, calculations guide, flash cards, the NEC and tabs",
    "jump-start-package": "a starter set of books and online practice",
    "complete-package": "the books, tabs and course together",
    "ultimate-combo": "the full study set plus the online test kit",
    "highlighted-tabbed": "the reference books already highlighted and permanently tabbed, ready for the exam room",
    "nec-course-package": "the study package plus an instructor-led NEC course",
    "live-training": "live virtual classes with an instructor plus self-study material",
    "rental-package": "the reference books on rental plus the online course, returned after your exam",
    "ultimate-rental": "highlighted and tabbed rental books, the online course and live training",
    "licensing-service": "help preparing and filing the license application",
    "the-1-package": "everything: exam prep, books, licensing paperwork and business setup",
    "ultimate-package": "the complete exam prep package",
    "exam-prep-package": "an exam prep package for an earlier code cycle",
    "other": "exam prep",
}
