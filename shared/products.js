/* =====================================================================
   PRODUCTS.JS  —  THE ONLY FILE YOU NEED TO EDIT
   ---------------------------------------------------------------------
   1. Replace every "PASTE_CHECKOUT_LINK_HERE" with your real checkout URL.
   2. Change names, prices and descriptions however you like.
   3. Add or remove products by copying/deleting a { ... } block.
   All five designs read from this file automatically.
   ===================================================================== */

window.SITE = {
  brand: "MasterPrep",
  tagline: "Master electrician exam prep",
  supportEmail: "support@example.com",
  // Shown in the "Built for your state" section. Edit freely.
  states: ["AK","AZ","CO","CT","DC","IA","MA","MT","NC","NM","NV","OK","SC","TN","TX","VA","WA"],
  // Current NEC editions mentioned on the pages
  codeNote: "Texas tests the 2023 NEC, Virginia the 2020 NEC, Wisconsin the 2023 NEC. Always match the edition in your candidate bulletin."
};

window.PRODUCTS = [
  {
    id: "quick-100",
    name: "Quick Start Pack",
    short: "100 practice questions",
    price: "$29.95",
    compareAt: "",
    badge: "",
    access: "30-day access",
    description:
      "A fast diagnostic of where you stand. One hundred master-level questions across the national NEC portion, each with a worked explanation and the code reference you should have found. Ideal if your exam is close and you need to find weak spots quickly.",
    features: [
      "100 master-level practice questions",
      "Explanation and code reference on every answer",
      "Timed mode mirrors the real exam clock",
      "Works on phone, tablet and desktop"
    ],
    checkout: "PASTE_CHECKOUT_LINK_HERE"
  },
  {
    id: "core-300",
    name: "Core 3-Pack",
    short: "300 questions in 3 full exams",
    price: "$54.95",
    compareAt: "$89.85",
    badge: "Save 39%",
    access: "60-day access",
    description:
      "Three complete simulated exams built around the topic weights published by PSI and state boards: services and feeders, grounding and bonding, conductors, raceways, motors and special occupancies. Take them timed and open-book, exactly as you will on test day.",
    features: [
      "3 full-length timed practice exams",
      "Weighted like real board outlines",
      "Progress tracking by topic",
      "Retake as many times as you want"
    ],
    checkout: "PASTE_CHECKOUT_LINK_HERE"
  },
  {
    id: "master-520",
    name: "Master Study Pack",
    short: "520 questions + readiness tracker",
    price: "$74.95",
    compareAt: "",
    badge: "Most popular",
    access: "90-day access",
    description:
      "The complete national-portion bank. Five hundred twenty questions sorted by topic and difficulty, a readiness score that tells you when you are consistently above the passing standard, and training mode that lets you drill one weak area at a time until it sticks.",
    features: [
      "520 questions sorted by topic and difficulty",
      "Readiness score shows when you are ready to book",
      "Training mode for drilling weak areas",
      "Timed test mode with real exam pacing",
      "Free diagnostic included"
    ],
    checkout: "PASTE_CHECKOUT_LINK_HERE"
  },
  {
    id: "calc-workshop",
    name: "Calculations Workshop",
    short: "Load, motor, box fill and voltage drop",
    price: "$39.95",
    compareAt: "",
    badge: "",
    access: "90-day access",
    description:
      "The calculations portion is where most candidates lose points. This workshop walks step by step through dwelling and commercial load calcs, motor circuits, transformer protection, box and raceway fill and voltage drop, then gives you timed problem sets to practice until the method is automatic.",
    features: [
      "Step-by-step decision sequences for every calc type",
      "Dwelling and commercial service calculations",
      "Motor, transformer and conductor sizing",
      "Timed problem sets with full solutions"
    ],
    checkout: "PASTE_CHECKOUT_LINK_HERE"
  },
  {
    id: "complete-850",
    name: "Complete Bundle",
    short: "850+ questions + calculations workshop",
    price: "$104.95",
    compareAt: "$144.85",
    badge: "Best value",
    access: "120-day access",
    description:
      "Everything in one place. More than 850 unique questions covering the full national portion, the Calculations Workshop, all simulated exams and the readiness tracker. Built for the twelve-week study plan: orientation, NEC navigation, calculations, mock exams, final review.",
    features: [
      "850+ unique practice questions",
      "Calculations Workshop included",
      "All full-length simulated exams",
      "Readiness tracker and error log",
      "Longest access window"
    ],
    checkout: "PASTE_CHECKOUT_LINK_HERE"
  }
];
