// Jewish Heritage Calendar — app.js
// Dynamically populates the homepage with today's community and region

// Short preview descriptions for 365 communities
// Major communities get custom text; all others get a generic description.
const COMMUNITY_PREVIEWS = {
  "jerusalem": "The eternal city, center of Jewish longing for three millennia — site of the Temple Mount, the Kotel, and the ancient City of David.",
  "safed": "High in the Galilean hills, Safed became the mystical capital of Kabbalah in the 16th century under Rabbi Yosef Karo and Rabbi Isaac Luria.",
  "tiberias": "On the western shore of the Sea of Galilee, Tiberias hosted the Jerusalem Talmud's final editing and remains one of Judaism's four holy cities.",
  "hebron": "Home of the Cave of Machpelah, burial site of the patriarchs and matriarchs, Hebron has maintained a continuous Jewish presence for millennia.",
  "jaffa": "Ancient Mediterranean port and gateway to the Land of Israel, transformed by 19th-century Zionist immigration into the gateway to modern Tel Aviv.",
  "haifa": "The Carmel mountain city that became a major center of Zionist settlement and, later, a model of Jewish-Arab coexistence in modern Israel.",
  "tel-aviv": "The first modern Hebrew city, founded on sand dunes in 1909, which grew to become the bustling metropolis at the heart of modern Israel.",
  "nazareth": "A Galilean city with a small but significant Jewish presence through the Talmudic era, when it was home to the priestly Hapizzez family.",
  "beit-shean": "Ancient crossroads city in the Jordan Valley, home to a Jewish community throughout the Byzantine era and site of elaborate synagogue mosaics.",
  "caesarea-maritima": "Herod's grand Mediterranean city served as the seat of Roman rule and a major center of Jewish-Gentile interaction in the Talmudic period.",
  "sura": "The Babylonian academy of Sura, founded by Rav in the 3rd century CE, became one of the two great centers shaping the Babylonian Talmud.",
  "pumbedita": "Sister academy to Sura, Pumbedita produced generations of Geonim whose rulings governed Jewish life across the Islamic world for 700 years.",
  "baghdad": "Capital of the Islamic caliphates and home to one of the world's great Jewish communities — over 100,000 souls with roots in the Biblical exile.",
  "babylon": "The ancient city where King Nebuchadnezzar brought the Jewish exiles in 586 BCE, giving birth to the most productive diaspora in Jewish history.",
  "nehardea": "The earliest great Babylonian Jewish academy, Nehardea trained scholars who would shape the emerging Oral Torah tradition in exile.",
  "tehran": "Modern capital of Iran and longtime home to the largest Jewish community in the Middle East outside Israel, tracing roots to the Persian period.",
  "isfahan": "The Safavid imperial capital once called 'Half the World,' Isfahan's ancient Jewish quarter endured persecutions and preserved unique Persian liturgy.",
  "bukhara": "The Silk Road jewel of Central Asia, Bukhara's Jewish community developed its own language, music, and textile traditions over two millennia.",
  "samarkand": "Timur's magnificent capital hosted a Bukharan Jewish community of weavers, merchants, and musicians famed throughout Central Asia.",
  "hamadan": "Ancient Ecbatana of the Persians, Hamadan is traditionally identified as the setting of the Purim story and site of Esther and Mordecai's tombs.",
  "cairo": "Egypt's capital became a medieval Jewish hub; the Ben Ezra Synagogue's hidden Geniza preserved 400,000 manuscript fragments for 1,000 years.",
  "alexandria": "The Hellenistic metropolis where Philo philosophized, the Torah was translated into Greek, and one of the ancient world's largest Jewish communities flourished.",
  "fez": "The royal city of Morocco where the first mellah (Jewish quarter) was established in 1438, hosting Sephardic refugees and ancient Berber-Jewish communities.",
  "djerba": "The Tunisian island whose El Ghriba synagogue, said to date to the First Temple era, draws pilgrims from across the Jewish world each Lag Ba'Omer.",
  "tunis": "Capital of ancient Carthage and medieval Tunisia, Tunis supported a Jewish community that produced the great Talmudic codifier Rabbenu Chananel.",
  "toledo": "The imperial city of Castile where Samuel HaNagid's successors built magnificent synagogues — El Transito and Santa Maria la Blanca still stand today.",
  "cordoba": "The Umayyad caliphate's jewel, birthplace of Maimonides, where Jewish philosophy, poetry, and science reached heights unsurpassed in the diaspora.",
  "granada": "Last bastion of Al-Andalus, Granada's Alhambra was home to the brilliant Samuel ibn Naghrela before the Golden Age gave way to the Reconquista.",
  "seville": "Andalusian capital where the great 1391 pogroms triggered mass conversions, creating the converso phenomenon that would haunt Spain for centuries.",
  "barcelona": "The medieval Crown of Aragon's capital sheltered a thriving Jewish community in the Call district until the devastating 1391 riots and expulsions.",
  "lisbon": "Capital of Portugal, where 100,000 Spanish Jewish refugees arrived in 1492, were forced into mass conversion in 1497, and became the first Marranos.",
  "istanbul": "Sultan Bayezid II's capital welcomed 150,000 Spanish Jewish exiles in 1492, creating a vast Ladino-speaking community that shaped Ottoman culture.",
  "salonika": "The 'Jerusalem of the Balkans' was a majority-Jewish city for 400 years, with Ladino as its commercial language and 30 synagogues serving each community of origin.",
  "sarajevo": "Bosnia's cosmopolitan capital sheltered Sephardic Jews from 1565 under Ottoman rule; its Haggadah is among the most beautiful Hebrew manuscripts.",
  "rhodes": "The island of Rhodes hosted a Sephardic Jewish community in its La Juderia district for 500 years, until the Nazi deportation of 1944.",
  "athens": "Home of the ancient Romaniote Jews, whose Greek-speaking community predates the Common Era and survived into the 20th century.",
  "istanbul-ashkenaz": "Istanbul's smaller Ashkenazic community coexisted with its far larger Sephardic counterpart, adding a northern European flavor to Ottoman Jewish life.",
  "mainz": "The ShUM city par excellence — home of Rabbenu Gershom 'Light of the Exile' and the great Maharam, until the Crusader massacres of 1096 shattered the community.",
  "worms": "Where Rashi studied and the great Rhenish community flourished before the First Crusade; the medieval Worms synagogue was rebuilt repeatedly after each destruction.",
  "amsterdam": "The 'Jerusalem of the North' welcomed Sephardic refugees and bred Spinoza; its Portuguese Synagogue (1675) remains the grandest 17th-century synagogue in Europe.",
  "frankfurt": "The Judengasse's crowded lanes produced the Rothschild banking dynasty and Samson Raphael Hirsch's neo-Orthodoxy in the shadow of the Frankfurt ghetto.",
  "berlin": "Moses Mendelssohn launched the Jewish Enlightenment here; 19th-century Berlin became a laboratory of Jewish modernity, emancipation, and cultural creativity.",
  "paris": "France's Jewish community, emancipated in 1791 as the first in Europe, built a vibrant culture from the Marais to the salons of the Third Republic.",
  "vienna": "Home to Herzl, Freud, Mahler, and Wittgenstein — Vienna's 200,000 Jews made the Habsburg capital a center of modern Jewish intellectual life.",
  "prague": "The Maharal's city — Prague's Josefov quarter, with its Old-New Synagogue (c. 1270) and the Old Jewish Cemetery, is the most evocative Jewish quarter in Europe.",
  "budapest": "The Dohány Street Synagogue, the world's second-largest, symbolizes Budapest's role as a great center of Reform and Neolog Judaism in the 19th century.",
  "krakow": "Royal capital of Poland and home to the great Kazimierz Jewish quarter, Krakow was a center of Torah scholarship, Hasidism, and Jewish printing.",
  "lublin": "The 'City of Torah Scholars,' Lublin's Maharsha and the famous Yeshivat Chachmei Lublin made it one of the foremost centers of Jewish learning in Europe.",
  "warsaw": "With 370,000 Jews — 30% of the city — Warsaw was the world's second-largest Jewish city, a center of Yiddish culture, Zionism, and the heroic 1943 Ghetto Uprising.",
  "vilna": "The 'Jerusalem of Lithuania,' home of the Vilna Gaon, YIVO Institute, and a Jewish cultural life of staggering richness destroyed in the Holocaust.",
  "bialystok": "A major textile city in northeastern Poland where Yiddish secular culture, labor movements, and Orthodox piety competed in a dense Jewish urban world.",
  "lodz": "Poland's industrial capital had a Jewish community of 230,000 — the second-largest Jewish ghetto under Nazi occupation, lasting until August 1944.",
  "lviv": "Habsburg Lemberg became interwar Polish Lwów — a center of Galician Jewish culture, Zionist politics, and Hebrew journalism before the Nazi destruction.",
  "odessa": "The cosmopolitan Black Sea port was the birthplace of modern Hebrew literature, secular Zionism, and Jewish organized crime — a city unlike any other.",
  "kiev": "Ukraine's capital city hosted a vibrant Jewish community, overshadowed forever by Babi Yar — the September 1941 ravine massacre of 33,771 Jews in two days.",
  "minsk": "Capital of Belarus and a major Pale of Settlement city, Minsk's Jewish community produced Bundist leaders, Hebrew poets, and revolutionary thinkers.",
  "kishinev": "The 1903 Kishinev pogrom shocked the world and accelerated the Zionist movement; Bialik immortalized it in his searing poem 'City of Slaughter.'",
  "london": "From the medieval martyrs of York to the East End's Ashkenazic immigrants, London's Jews built a community that produced Disraeli, the Rothschilds, and Isaiah Berlin.",
  "york": "The Clifford's Tower massacre of March 16–17, 1190, when 150 Jews died rather than submit to baptism, remains a defining moment of medieval Anglo-Jewish history.",
  "new-york": "The greatest Jewish city in history — two million Jews transformed the Lower East Side, Broadway, and American intellectual life across the 20th century.",
  "newport": "George Washington wrote to Newport's Jewish congregation in 1790 that 'the Government of the United States gives to bigotry no sanction,' a founding promise.",
  "philadelphia": "Home of Mikveh Israel congregation (1740), Philadelphia's Jews participated in the American Revolution and built one of the first great North American communities.",
  "boston": "New England's Jewish community, centered in Roxbury and Brookline, grew from colonial Sephardic merchants to the great immigrant communities of the 20th century.",
  "buenos-aires": "The largest Jewish community in Latin America — 300,000 strong — shaped by Eastern European immigration from 1890 onward and the Baron Hirsch colonies.",
  "montreal": "Canada's French-speaking metropolis hosted a major Jewish community in Mile End and Outremont, producing Mordecai Richler and a distinctive Canadian Jewish culture.",
  "toronto": "Canada's largest Jewish community, centered in Forest Hill and North York, became one of the most vibrant in North America in the postwar decades.",
  "sao-paulo": "Brazil's economic capital is home to the largest Jewish community in Latin America — 60,000 Jews whose roots span Sephardic Brazil to Eastern European immigration.",
  "recife": "The first Jewish community in the Americas flourished in Dutch-held Recife, Brazil from 1630–1654, before fleeing to New Amsterdam (New York) after Portuguese reconquest."
};

// Default description for communities without a specific preview
const DEFAULT_PREVIEW = "One of 365 historic Jewish communities featured in the Heritage Calendar — each telling a unique story of faith, culture, survival, and memory.";

// Get a preview description for a community
function getCommunityPreview(communityId) {
  return COMMUNITY_PREVIEWS[communityId] || DEFAULT_PREVIEW;
}

// Calculate day of year (1-365)
function getDayOfYear(date) {
  const start = new Date(date.getFullYear(), 0, 0);
  const diff = date - start;
  const oneDay = 1000 * 60 * 60 * 24;
  return Math.floor(diff / oneDay);
}

// Get month from day of year (1-12)
function getMonthFromDay(day) {
  const year = new Date().getFullYear();
  const date = new Date(year, 0, day);
  return date.getMonth() + 1;
}

// Country name to flag emoji
function getCountryEmoji(country) {
  const flags = {
    "Israel": "🇮🇱",
    "Palestinian Territories": "🇵🇸",
    "Iraq": "🇮🇶",
    "Syria": "🇸🇾",
    "Turkey": "🇹🇷",
    "Iran": "🇮🇷",
    "Uzbekistan": "🇺🇿",
    "Tajikistan": "🇹🇯",
    "Turkmenistan": "🇹🇲",
    "Afghanistan": "🇦🇫",
    "Egypt": "🇪🇬",
    "Libya": "🇱🇾",
    "Tunisia": "🇹🇳",
    "Algeria": "🇩🇿",
    "Morocco": "🇲🇦",
    "Spain": "🇪🇸",
    "Portugal": "🇵🇹",
    "France": "🇫🇷",
    "Gibraltar": "🇬🇮",
    "Greece": "🇬🇷",
    "Bulgaria": "🇧🇬",
    "Serbia": "🇷🇸",
    "Bosnia": "🇧🇦",
    "Croatia": "🇭🇷",
    "Romania": "🇷🇴",
    "Albania": "🇦🇱",
    "North Macedonia": "🇲🇰",
    "Germany": "🇩🇪",
    "Netherlands": "🇳🇱",
    "Belgium": "🇧🇪",
    "Austria": "🇦🇹",
    "Czech Republic": "🇨🇿",
    "Slovakia": "🇸🇰",
    "Hungary": "🇭🇺",
    "Ukraine": "🇺🇦",
    "Poland": "🇵🇱",
    "Lithuania": "🇱🇹",
    "Belarus": "🇧🇾",
    "Latvia": "🇱🇻",
    "Estonia": "🇪🇪",
    "Russia": "🇷🇺",
    "Moldova": "🇲🇩",
    "United Kingdom": "🇬🇧",
    "Ireland": "🇮🇪",
    "United States": "🇺🇸",
    "Canada": "🇨🇦",
    "Argentina": "🇦🇷",
    "Brazil": "🇧🇷",
    "Mexico": "🇲🇽",
    "Uruguay": "🇺🇾",
    "Chile": "🇨🇱",
    "Colombia": "🇨🇴",
    "Peru": "🇵🇪",
    "Cuba": "🇨🇺",
    "Jamaica": "🇯🇲",
    "Barbados": "🇧🇧",
    "Suriname": "🇸🇷",
    "Panama": "🇵🇦",
    "Curaçao": "🇨🇼",
    "China": "🇨🇳",
    "Kyrgyzstan": "🇰🇬"
  };
  return flags[country] || "🌍";
}

// Format date nicely
function formatDate(date) {
  return date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
}

// Format short date
function formatShortDate(date) {
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// Find which region covers a given month
function getRegionForMonth(regions, month) {
  return regions.find(r => r.month === month) || regions[0];
}

// Populate the hero section with today's community
function populateHero(community, regions) {
  const today = new Date();
  const dayOfYear = getDayOfYear(today);
  const container = document.getElementById('hero-community');
  const loading = document.getElementById('hero-loading');

  if (loading) loading.style.display = 'none';

  if (!container) return;

  const preview = getCommunityPreview(community.id);
  const month = getMonthFromDay(dayOfYear);
  const region = getRegionForMonth(regions, month);
  const countryFlag = getCountryEmoji(community.country || (region.modernCountries && region.modernCountries[0]));
  const regionName = region ? region.name : (community.region || 'Heritage Region');
  const countryName = community.country || (region && region.modernCountries ? region.modernCountries[0] : '');

  container.innerHTML = `
    <span class="hero-badge">Heritage Day ${dayOfYear} of 365</span>
    <h1>Today: ${community.name} Heritage Day</h1>
    <p class="hero-subheading">${regionName} · ${countryFlag} ${countryName}</p>
    <p class="hero-preview">${preview.slice(0, 200)}${preview.length > 200 ? '…' : ''}</p>
    <a href="community/${community.id}.html" class="hero-button">Read Full Heritage Story →</a>
  `;
  container.style.display = 'block';
}

// Populate the "This Month" section
function populateThisMonth(region) {
  const container = document.getElementById('this-month-region');
  if (!container) return;

  const factsHtml = (region.keyFacts || []).map(f =>
    `<li>→ ${f}</li>`
  ).join('');

  container.innerHTML = `
    <div class="region-card" style="border-left-color: ${region.color};">
      <div class="region-month" style="color: ${region.color};">${region.monthName}</div>
      <h3>${region.name}</h3>
      <p class="region-tagline">"${region.tagline}"</p>
      <p style="font-size:0.9rem; color:#6b5d4f;">${region.communities} Communities This Month</p>
    </div>
    <div class="region-description">
      <h4>About This Region</h4>
      <p>${region.heroDescription}</p>
      <ul class="key-facts">${factsHtml}</ul>
      <a href="region/${region.id}.html" style="display:inline-block; margin-top:1.5rem; color:${region.color}; font-weight:600;">
        Explore ${region.monthName} Communities →
      </a>
    </div>
  `;
}

// Populate the upcoming heritage days row
function populateUpcoming(communities, today) {
  const container = document.getElementById('upcoming-days');
  if (!container) return;

  const todayDayOfYear = getDayOfYear(today);

  // Get the next 7 days
  const upcoming = [];
  for (let i = 1; i <= 7; i++) {
    const dayNum = todayDayOfYear + i;
    const adjustedDay = ((dayNum - 1) % 365) + 1;
    const community = communities.find(c => (c.day || c.dayOfYear) === adjustedDay);
    if (community) {
      const date = new Date(today.getFullYear(), 0, adjustedDay);
      upcoming.push({ community, date, day: adjustedDay });
    }
  }

  if (upcoming.length === 0) {
    container.innerHTML = '<p style="color:#6b5d4f; padding:1rem;">Upcoming schedule loading…</p>';
    return;
  }

  container.innerHTML = upcoming.map(({ community, date, day }) => {
    const flag = getCountryEmoji(community.country || '');
    return `
      <div class="upcoming-card" onclick="location.href='community/${community.id}.html'">
        <div class="upcoming-day">${day}</div>
        <div class="upcoming-date">${formatShortDate(date)}</div>
        <div class="upcoming-community">${community.name}</div>
        <div class="upcoming-country">${flag} ${community.country || ''}</div>
      </div>
    `;
  }).join('');
}

// Populate the 12-month browse grid
function populateMonthBrowse(regions) {
  const container = document.getElementById('month-browse');
  if (!container) return;

  const today = new Date();
  const currentMonth = today.getMonth() + 1;

  container.innerHTML = regions.map(region => {
    const isCurrentMonth = region.month === currentMonth;
    return `
      <div class="month-tile" style="border-left-color: ${region.color}; ${isCurrentMonth ? 'box-shadow: 0 4px 20px rgba(0,0,0,0.15); outline: 2px solid ' + region.color + ';' : ''}"
           onclick="location.href='region/${region.id}.html'">
        <div class="month-name" style="color: ${region.color};">${region.monthName}</div>
        <div class="month-region">${region.name}</div>
        <div class="month-communities" style="color: ${region.color};">${region.communities} Communities</div>
        ${isCurrentMonth ? '<div style="font-size:0.75rem; color:#c9a227; font-weight:600; margin-top:0.5rem;">▶ THIS MONTH</div>' : ''}
      </div>
    `;
  }).join('');
}

// Show an error in a container
function showError(containerId, message) {
  const el = document.getElementById(containerId);
  if (el) {
    el.innerHTML = `<p style="color:#922b21; padding:1rem; font-style:italic;">${message}</p>`;
    el.style.display = 'block';
  }
}

// Main initialization
document.addEventListener('DOMContentLoaded', async () => {
  const today = new Date();
  const dayOfYear = getDayOfYear(today);

  // Update current date display
  const dateEl = document.getElementById('current-date');
  if (dateEl) dateEl.textContent = formatDate(today);

  // Show loading skeleton
  const heroLoading = document.getElementById('hero-loading');
  const heroContent = document.getElementById('hero-community');
  if (heroLoading) heroLoading.style.display = 'block';
  if (heroContent) heroContent.style.display = 'none';

  try {
    // Fetch both data files in parallel
    const [communitiesRes, regionsRes] = await Promise.all([
      fetch('data/communities.json'),
      fetch('data/regions.json')
    ]);

    // Graceful fallback if communities.json doesn't exist yet
    let communities = [];
    let regions = [];

    if (communitiesRes.ok) {
      communities = await communitiesRes.json();
    } else {
      console.warn('communities.json not yet available');
    }

    if (regionsRes.ok) {
      regions = await regionsRes.json();
    } else {
      throw new Error('Could not load regions.json');
    }

    // Determine today's community
    const todayCommunity = communities.find(c => (c.day || c.dayOfYear) === dayOfYear);
    const currentMonth = today.getMonth() + 1;
    const currentRegion = getRegionForMonth(regions, currentMonth);

    // Hide loading skeleton
    if (heroLoading) heroLoading.style.display = 'none';

    // Populate sections
    if (todayCommunity) {
      populateHero(todayCommunity, regions);
    } else {
      // Fallback: show region info in hero
      if (heroContent) {
        heroContent.innerHTML = `
          <span class="hero-badge">Heritage Day ${dayOfYear} of 365</span>
          <h1>${currentRegion ? currentRegion.name : 'Jewish Heritage Calendar'}</h1>
          <p class="hero-subheading">${currentRegion ? currentRegion.tagline : '365 communities, one per day'}</p>
          <p class="hero-preview">Explore Jewish heritage communities from across the world, one per day throughout the year.</p>
          <a href="regions.html" class="hero-button">Explore All Regions →</a>
        `;
        heroContent.style.display = 'block';
      }
    }

    if (currentRegion) {
      populateThisMonth(currentRegion);
    }

    if (communities.length > 0) {
      populateUpcoming(communities, today);
    }

    if (regions.length > 0) {
      populateMonthBrowse(regions);
    }

    // Update footer year
    const footerYear = document.querySelector('footer p');
    if (footerYear) {
      footerYear.textContent = `Celebrating 365 Jewish Communities Worldwide · ${today.getFullYear()}`;
    }

  } catch (err) {
    console.error('Error loading calendar data:', err);
    if (heroLoading) heroLoading.style.display = 'none';
    showError('hero-community', 'Heritage Calendar data is loading — please check back shortly.');
    showError('this-month-region', 'Region data could not be loaded.');
    showError('upcoming-days', 'Upcoming days will appear once communities.json is generated.');
    showError('month-browse', 'Month browser loading…');

    // Still try to populate month browse from fallback
    try {
      const regionsRes = await fetch('data/regions.json');
      if (regionsRes.ok) {
        const regions = await regionsRes.json();
        populateMonthBrowse(regions);
        const currentMonth = new Date().getMonth() + 1;
        const currentRegion = getRegionForMonth(regions, currentMonth);
        if (currentRegion) populateThisMonth(currentRegion);
      }
    } catch (e) {
      // silently fail
    }
  }
});
