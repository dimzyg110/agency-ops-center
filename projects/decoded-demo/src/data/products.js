const now = Date.now()

const R2 = 'https://pub-12a9e278dc6d454fa3a74b79a8b8e63d.r2.dev/demo'
const IA = 'https://ia800608.us.archive.org/13/items/darkambient_201908'

export const DROP_END_TIME = now + 3 * 86400000 + 14 * 3600000

export const products = [
  {
    id: 1,
    name: "NOIR\nSTRATA",
    subtitle: "Black Top",
    price: 120,
    tag: "Decoded Noir",
    materials: "Heavyweight cotton · 380gsm",
    edition: 50,
    dropEnd: now + 2 * 3600000 + 34 * 60000,
    fireCount: 2412,
    skullCount: 891,
    video: `${R2}/noir-strata.mp4`,
    music: `${IA}/Crime.mp3`,
    gradient: `
      radial-gradient(ellipse 80% 60% at 25% 85%, rgba(90,50,160,0.18) 0%, transparent 60%),
      radial-gradient(ellipse 60% 50% at 75% 15%, rgba(201,168,76,0.06) 0%, transparent 50%),
      radial-gradient(circle at 50% 50%, rgba(30,20,50,0.5) 0%, transparent 70%),
      linear-gradient(170deg, #0D0D0D 0%, #110a1e 35%, #0D0D0D 100%)
    `,
  },
  {
    id: 2,
    name: "HAND\nOF GOD",
    subtitle: null,
    price: 150,
    tag: "Limited to 50",
    materials: "French terry · 420gsm",
    edition: 35,
    dropEnd: now + 5 * 3600000 + 12 * 60000,
    fireCount: 1837,
    skullCount: 643,
    video: `${R2}/hand-of-god.mp4`,
    music: `${IA}/Gloomy.mp3`,
    gradient: `
      radial-gradient(ellipse 70% 55% at 70% 80%, rgba(20,100,100,0.15) 0%, transparent 55%),
      radial-gradient(ellipse 50% 45% at 20% 20%, rgba(201,168,76,0.05) 0%, transparent 45%),
      radial-gradient(circle at 45% 60%, rgba(15,35,40,0.4) 0%, transparent 65%),
      linear-gradient(190deg, #111 0%, #0a1a1e 40%, #0D0D0D 100%)
    `,
  },
  {
    id: 3,
    name: "ALL\nGLORY",
    subtitle: "Black",
    price: 140,
    tag: "Drop Exclusive",
    materials: "Organic cotton · 320gsm",
    edition: 75,
    dropEnd: now + 12 * 3600000 + 5 * 60000,
    fireCount: 3291,
    skullCount: 1204,
    video: `${R2}/all-glory-black.mp4`,
    music: `${IA}/Nightmare.mp3`,
    gradient: `
      radial-gradient(ellipse 75% 50% at 60% 85%, rgba(140,30,30,0.12) 0%, transparent 55%),
      radial-gradient(ellipse 55% 40% at 30% 10%, rgba(201,168,76,0.04) 0%, transparent 45%),
      radial-gradient(circle at 55% 45%, rgba(40,15,15,0.4) 0%, transparent 65%),
      linear-gradient(175deg, #0D0D0D 0%, #1a0c0c 38%, #0D0D0D 100%)
    `,
  },
  {
    id: 4,
    name: "BROKE\nTEE",
    subtitle: null,
    price: 125,
    tag: "806 Exclusive",
    materials: "Japanese cotton · 280gsm",
    edition: 100,
    dropEnd: now + 1 * 3600000 + 48 * 60000,
    fireCount: 967,
    skullCount: 412,
    video: `${R2}/broke-tee.mp4`,
    music: `${IA}/Valhalla.mp3`,
    gradient: `
      radial-gradient(ellipse 65% 55% at 35% 80%, rgba(25,35,100,0.14) 0%, transparent 55%),
      radial-gradient(ellipse 50% 40% at 80% 25%, rgba(201,168,76,0.06) 0%, transparent 45%),
      radial-gradient(circle at 50% 55%, rgba(15,15,45,0.45) 0%, transparent 65%),
      linear-gradient(185deg, #131315 0%, #0c0c20 40%, #0D0D0D 100%)
    `,
  },
  {
    id: 5,
    name: "DECODED\nANGELS",
    subtitle: "Hoodie",
    price: 120,
    tag: "Only 30 Made",
    materials: "Premium fleece · 450gsm",
    edition: 40,
    dropEnd: now + 8 * 3600000 + 22 * 60000,
    fireCount: 2076,
    skullCount: 583,
    video: `${R2}/angels-hoodie.mp4`,
    music: `${IA}/Nightmares.mp3`,
    gradient: `
      radial-gradient(ellipse 70% 55% at 45% 85%, rgba(120,80,20,0.14) 0%, transparent 55%),
      radial-gradient(ellipse 55% 40% at 70% 15%, rgba(201,168,76,0.07) 0%, transparent 45%),
      radial-gradient(circle at 50% 55%, rgba(40,30,10,0.4) 0%, transparent 65%),
      linear-gradient(180deg, #121010 0%, #1a140a 40%, #0D0D0D 100%)
    `,
  },
]
