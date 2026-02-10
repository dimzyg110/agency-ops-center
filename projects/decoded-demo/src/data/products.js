const now = Date.now()

export const products = [
  {
    id: 1,
    name: "MIDNIGHT\nBOMBER",
    subtitle: "Jacket",
    price: 285,
    tag: "Limited to 50",
    dropEnd: now + 2 * 3600000 + 34 * 60000,
    fireCount: 2412,
    skullCount: 891,
    gradient: `
      radial-gradient(ellipse 80% 60% at 25% 85%, rgba(90,50,160,0.18) 0%, transparent 60%),
      radial-gradient(ellipse 60% 50% at 75% 15%, rgba(201,168,76,0.06) 0%, transparent 50%),
      radial-gradient(circle at 50% 50%, rgba(30,20,50,0.5) 0%, transparent 70%),
      linear-gradient(170deg, #0D0D0D 0%, #110a1e 35%, #0D0D0D 100%)
    `,
  },
  {
    id: 2,
    name: "PHANTOM\nHOODIE",
    subtitle: null,
    price: 165,
    tag: "Drop Exclusive",
    dropEnd: now + 5 * 3600000 + 12 * 60000,
    fireCount: 1837,
    skullCount: 643,
    gradient: `
      radial-gradient(ellipse 70% 55% at 70% 80%, rgba(20,100,100,0.15) 0%, transparent 55%),
      radial-gradient(ellipse 50% 45% at 20% 20%, rgba(201,168,76,0.05) 0%, transparent 45%),
      radial-gradient(circle at 45% 60%, rgba(15,35,40,0.4) 0%, transparent 65%),
      linear-gradient(190deg, #111 0%, #0a1a1e 40%, #0D0D0D 100%)
    `,
  },
  {
    id: 3,
    name: "GHOST\nLINE TEE",
    subtitle: null,
    price: 85,
    tag: "Restocked by Demand",
    dropEnd: now + 12 * 3600000 + 5 * 60000,
    fireCount: 3291,
    skullCount: 1204,
    gradient: `
      radial-gradient(ellipse 75% 50% at 60% 85%, rgba(140,30,30,0.12) 0%, transparent 55%),
      radial-gradient(ellipse 55% 40% at 30% 10%, rgba(201,168,76,0.04) 0%, transparent 45%),
      radial-gradient(circle at 55% 45%, rgba(40,15,15,0.4) 0%, transparent 65%),
      linear-gradient(175deg, #0D0D0D 0%, #1a0c0c 38%, #0D0D0D 100%)
    `,
  },
  {
    id: 4,
    name: "VAULT\nLOCK CAP",
    subtitle: null,
    price: 55,
    tag: "Members Only",
    dropEnd: now + 1 * 3600000 + 48 * 60000,
    fireCount: 967,
    skullCount: 412,
    gradient: `
      radial-gradient(ellipse 65% 55% at 35% 80%, rgba(25,35,100,0.14) 0%, transparent 55%),
      radial-gradient(ellipse 50% 40% at 80% 25%, rgba(201,168,76,0.06) 0%, transparent 45%),
      radial-gradient(circle at 50% 55%, rgba(15,15,45,0.45) 0%, transparent 65%),
      linear-gradient(185deg, #131315 0%, #0c0c20 40%, #0D0D0D 100%)
    `,
  },
  {
    id: 5,
    name: "NOIR\nRUNNER",
    subtitle: null,
    price: 220,
    tag: "Gone in 48 Hours",
    dropEnd: now + 47 * 3600000 + 59 * 60000,
    fireCount: 1545,
    skullCount: 728,
    gradient: `
      radial-gradient(ellipse 75% 50% at 55% 85%, rgba(20,80,40,0.13) 0%, transparent 55%),
      radial-gradient(ellipse 45% 40% at 15% 15%, rgba(201,168,76,0.05) 0%, transparent 45%),
      radial-gradient(circle at 50% 50%, rgba(10,30,15,0.4) 0%, transparent 65%),
      linear-gradient(165deg, #0D0D0D 0%, #0a150c 38%, #0D0D0D 100%)
    `,
  },
  {
    id: 6,
    name: "THE\nCONFESSION",
    subtitle: "Crewneck",
    price: 145,
    tag: "Vault Lock Eligible",
    dropEnd: now + 8 * 3600000 + 22 * 60000,
    fireCount: 2076,
    skullCount: 583,
    gradient: `
      radial-gradient(ellipse 70% 55% at 45% 85%, rgba(120,80,20,0.14) 0%, transparent 55%),
      radial-gradient(ellipse 55% 40% at 70% 15%, rgba(201,168,76,0.07) 0%, transparent 45%),
      radial-gradient(circle at 50% 55%, rgba(40,30,10,0.4) 0%, transparent 65%),
      linear-gradient(180deg, #121010 0%, #1a140a 40%, #0D0D0D 100%)
    `,
  },
]
