const now = Date.now()

const R2 = 'https://pub-12a9e278dc6d454fa3a74b79a8b8e63d.r2.dev/demo'

export const DROP_END_TIME = now + 3 * 86400000 + 14 * 3600000

export const products = [
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
    video: `${import.meta.env.BASE_URL}videos/broke-tee.mp4`,
    music: `${import.meta.env.BASE_URL}audio/song4.mp3`,
    songName: "The Weeknd — Hurt You / I Was Never There",
    gradient: `
      radial-gradient(ellipse 65% 55% at 35% 80%, rgba(30,30,30,0.14) 0%, transparent 55%),
      radial-gradient(ellipse 50% 40% at 80% 25%, rgba(60,60,60,0.06) 0%, transparent 45%),
      radial-gradient(circle at 50% 55%, rgba(20,20,20,0.45) 0%, transparent 65%),
      linear-gradient(185deg, #131313 0%, #0e0e0e 40%, #0D0D0D 100%)
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
    video: `${import.meta.env.BASE_URL}videos/all-glory-black.mp4`,
    music: `${import.meta.env.BASE_URL}audio/song3.mp3`,
    songName: "The Weeknd ft. Playboi Carti — Timeless",
    gradient: `
      radial-gradient(ellipse 75% 50% at 60% 85%, rgba(35,35,35,0.12) 0%, transparent 55%),
      radial-gradient(ellipse 55% 40% at 30% 10%, rgba(50,50,50,0.04) 0%, transparent 45%),
      radial-gradient(circle at 55% 45%, rgba(25,25,25,0.4) 0%, transparent 65%),
      linear-gradient(175deg, #0D0D0D 0%, #121212 38%, #0D0D0D 100%)
    `,
  },
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
    video: `${import.meta.env.BASE_URL}videos/noir-strata.mp4`,
    music: `${import.meta.env.BASE_URL}audio/song1.mp3`,
    songName: "The Weeknd ft. Playboi Carti — Timeless",
    gradient: `
      radial-gradient(ellipse 80% 60% at 25% 85%, rgba(40,40,40,0.18) 0%, transparent 60%),
      radial-gradient(ellipse 60% 50% at 75% 15%, rgba(55,55,55,0.06) 0%, transparent 50%),
      radial-gradient(circle at 50% 50%, rgba(25,25,25,0.5) 0%, transparent 70%),
      linear-gradient(170deg, #0D0D0D 0%, #111111 35%, #0D0D0D 100%)
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
    video: `${import.meta.env.BASE_URL}videos/hand-of-god.mp4`,
    music: `${import.meta.env.BASE_URL}audio/song2.mp3`,
    songName: "The Weeknd ft. Playboi Carti — Timeless",
    gradient: `
      radial-gradient(ellipse 70% 55% at 70% 80%, rgba(35,35,35,0.15) 0%, transparent 55%),
      radial-gradient(ellipse 50% 45% at 20% 20%, rgba(50,50,50,0.05) 0%, transparent 45%),
      radial-gradient(circle at 45% 60%, rgba(20,20,20,0.4) 0%, transparent 65%),
      linear-gradient(190deg, #111 0%, #0f0f0f 40%, #0D0D0D 100%)
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
    video: `${import.meta.env.BASE_URL}videos/angels-hoodie.mp4`,
    music: `${import.meta.env.BASE_URL}audio/song5.mp3`,
    songName: "The Weeknd — Hurt You / I Was Never There",
    gradient: `
      radial-gradient(ellipse 70% 55% at 45% 85%, rgba(30,30,30,0.14) 0%, transparent 55%),
      radial-gradient(ellipse 55% 40% at 70% 15%, rgba(50,50,50,0.07) 0%, transparent 45%),
      radial-gradient(circle at 50% 55%, rgba(25,25,25,0.4) 0%, transparent 65%),
      linear-gradient(180deg, #121212 0%, #101010 40%, #0D0D0D 100%)
    `,
  },
]
