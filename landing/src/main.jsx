import React, { useRef, useState } from "react";
import { createRoot, hydrateRoot } from "react-dom/client";
import "./styles.css";
import { Pricing } from "./pricing.jsx";
import { ContentProvider, ContentText, useContent } from "./content.jsx";
function Icon({ name = "arrow", size = 20 }) {
  const paths = {
    arrow: (
      <>
        <path d="M4 12h16M14 6l6 6-6 6" />
      </>
    ),
    pin: (
      <>
        <path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 1 1 14 0Z" />
        <circle cx="12" cy="10" r="2" />
      </>
    ),
    shield: (
      <>
        <path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z" />
        <path d="m8 12 3 3 5-6" />
      </>
    ),
    close: <path d="m6 6 12 12M6 18 18 6" />,
    menu: <path d="M4 7h16M4 12h16M4 17h16" />,
    down: <path d="M12 3v16m-6-6 6 6 6-6M4 21h16" />,
  };
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  );
}
function Slider() {
  const { t } = useContent();
  const [value, setValue] = useState(0),
    [done, setDone] = useState(false);
  const track = useRef(null),
    drag = useRef(null);
  function finish() {
    setDone(true);
    drag.current = null;
  }
  function move(e) {
    if (drag.current === null || done) return;
    const max = track.current.clientWidth - 64;
    const scale =
      track.current.getBoundingClientRect().width / track.current.clientWidth;
    const x = Math.max(0, Math.min(max, (e.clientX - drag.current) / scale));
    setValue(x);
    if (x >= max) finish();
  }
  return (
    <div className="slider-demo">
      <div ref={track} className={"sos-track " + (done ? "complete" : "")}>
        <span className="slider-label">
          {done ? t("main.extra.168") : t("main.extra.169")} <span>› › ›</span>
        </span>
        <button
          className="sos-knob"
          aria-label="Демо SOS: перетащить вправо"
          style={{ transform: `translateX(${value}px)` }}
          onPointerDown={(e) => {
            if (done) return;
            const scale =
              track.current.getBoundingClientRect().width /
              track.current.clientWidth;
            drag.current = e.clientX - value * scale;
            e.currentTarget.setPointerCapture(e.pointerId);
          }}
          onPointerMove={move}
          onPointerUp={() => {
            drag.current = null;
            if (!done) setValue(0);
          }}
          onPointerCancel={() => {
            drag.current = null;
            if (!done) setValue(0);
          }}
        >
          SOS
        </button>
      </div>
      <div className="slider-status" aria-live="polite">
        {done ? (
          <>
            <span><ContentText name="main.extra.98" /></span>
            <button
              onClick={() => {
                setDone(false);
                setValue(0);
              }}
            ><ContentText name="main.extra.99" /></button>
          </>
        ) : (
          <span><ContentText name="main.extra.100" /></span>
        )}
      </div>
    </div>
  );
}
function CityMap() {
  return (
    <div className="city-map">
      <iframe
        className="map-svg osm-map"
        title="OpenStreetMap: демонстрационная точка в Оше"
        src="https://www.openstreetmap.org/export/embed.html?bbox=72.797%2C40.504%2C72.835%2C40.527&layer=mapnik&marker=40.5133%2C72.8161"
        loading="lazy"
        referrerPolicy="strict-origin-when-cross-origin"
      />
      <div className="map-top">
        <span>
          <i /><ContentText name="main.extra.104" /></span>
        <span><ContentText name="main.extra.105" /></span>
      </div>
      <div className="map-signal">
        <span className="signal-dot" />
        <div>
          <b><ContentText name="main.extra.106" /></b>
          <small><ContentText name="main.extra.107" /></small>
        </div>
        <span className="signal-time"><ContentText name="main.extra.108" /></span>
      </div>
      <div className="map-control">
        <Icon name="shield" />
        <span><ContentText name="main.extra.109" /></span>
      </div>
      <div className="map-bottom">
        <span><ContentText name="main.extra.110" /></span>
        <Icon name="pin" size={16} />
      </div>
    </div>
  );
}
function ProductPreview({ id }) {
  if (id === "personal")
    return (
      <div className="personal-preview">
        <div className="preview-heading">
          <b>QORGO</b>
          <span><ContentText name="main.extra.111" /></span>
        </div>
        <div className="personal-head">
          <span><ContentText name="main.extra.112" /></span>
          <h3><ContentText name="main.extra.113" /><br /><ContentText name="main.extra.114" /></h3>
        </div>
        <div className="family-row">
          <span className="avatar"><ContentText name="main.extra.115" /></span>
          <span className="avatar"><ContentText name="main.extra.116" /></span>
          <span><ContentText name="main.extra.117" /></span>
          <Icon size={16} />
        </div>
        <div className="try-label"><ContentText name="main.extra.118" /></div>
        <Slider />
      </div>
    );
  if (id === "x")
    return (
      <div className="terminals-preview">
        <div className="terminal">
          <b>
            QORGO <small>X LITE</small>
          </b>
          <div className="speaker">
            •••••••
            <br />
            •••••••
            <br />
            •••••••
          </div>
          <div className="physical-sos">SOS</div>
          <span><ContentText name="main.extra.119" /></span>
        </div>
        <div className="terminal mini">
          <b>
            QORGO <small>X MINI</small>
          </b>
          <div className="physical-sos">SOS</div>
          <span><ContentText name="main.extra.120" /></span>
        </div>
        <p><ContentText name="main.extra.121" /></p>
      </div>
    );
  return (
    <div className="control-preview">
      <div className="preview-heading">
        <b>QORGO Control</b>
        <span><ContentText name="main.extra.122" /></span>
      </div>
      <div className="control-alert">
        <span className="signal-dot" /><ContentText name="main.extra.123" /><span><ContentText name="main.extra.124" /></span>
      </div>
      <dl>
        <div>
          <dt><ContentText name="main.extra.125" /></dt>
          <dd><ContentText name="main.extra.126" /></dd>
        </div>
        <div>
          <dt><ContentText name="main.extra.127" /></dt>
          <dd><ContentText name="main.extra.128" /></dd>
        </div>
        <div>
          <dt><ContentText name="main.extra.129" /></dt>
          <dd><ContentText name="main.extra.130" /></dd>
        </div>
      </dl>
      <div className="incident-route">
        <i />
        <span><ContentText name="main.extra.131" /></span>
        <i />
        <span><ContentText name="main.extra.132" /></span>
      </div>
      <p><ContentText name="main.extra.133" /></p>
    </div>
  );
}
function Phone() {
  return (
    <div className="phone">
      <div className="phone-status">
        <span>9:41</span>
        <i />
        <span>▮▮▮</span>
      </div>
      <div className="phone-radar">
        <i />
        <i />
        <i />
        <img src="/brand/qorgo.svg" alt="QORGO" />
      </div>
      <div className="phone-name">
        QORGO<span><ContentText name="main.extra.134" /></span>
      </div>
      <div className="phone-demo">
        <Slider />
      </div>
      <div className="phone-nav">
        <Icon name="shield" />
        <Icon name="pin" />
        <span>◷</span>
      </div>
    </div>
  );
}
function Landing() {
  const { content, t } = useContent();
  const [menu, setMenu] = useState(false),
    [paused, setPaused] = useState(false);
  return (
    <>
      <a className="skip-link" href={content.links["link.1"] ?? "#main"}><ContentText name="main.001" /></a>
      <header>
        <a className="brand" href={content.links["link.2"] ?? "#"}>
          <img src="/brand/qorgo-dark.svg" alt="" />
          <span>qorgo</span>
        </a>
        <nav className={menu ? "open" : ""} aria-label="Основная навигация">
          {[
            ["#how", t("cards.001")],
            ["#response", t("cards.002")],
            ["#features", t("cards.003")],
            ["#pricing", t("cards.004")],
            ["#pilot", t("cards.005")],
            ["#faq", "FAQ"],
          ].map(([href, name]) => (
            <a href={content.links[`nav.${href.slice(1)}`] ?? href} key={href} onClick={() => setMenu(false)}>
              {name}
            </a>
          ))}
        </nav>
        <a href={content.links["link.3"] ?? "#partnership"} className="button header-cta">
          <Icon name="down" size={16} /><ContentText name="main.extra.135" /></a>
        <button
          className="menu-toggle"
          onClick={() => setMenu(!menu)}
          aria-label={menu ? "Закрыть меню" : "Открыть меню"}
          aria-expanded={menu}
        >
          <Icon name={menu ? "close" : "menu"} />
        </button>
      </header>
      <main id="main">
        <section className="hero">
          <div className="hero-copy">
            <h1><ContentText name="main.002" /></h1>
            <p><ContentText name="main.003" /></p>
            <a className="button" href={content.links["link.4"] ?? "#features"}><ContentText name="main.extra.136" /><Icon />
            </a>
          </div>
          <div className="floating-note note-one">
            <span className="note-avatar">
              <Icon name="shield" />
            </span>
            <div>
              <b><ContentText name="main.004" /></b>
              <small><ContentText name="main.005" /></small>
            </div>
          </div>
          <div className="floating-note note-two">
            <span className="note-avatar alert-avatar">
              <Icon name="pin" />
            </span>
            <div>
              <b><ContentText name="main.006" /></b>
              <small><ContentText name="main.007" /></small>
            </div>
          </div>
          <Phone />
          <div className="hero-facts">
            <div>
              <b>1</b>
              <span><ContentText name="main.008" /></span>
            </div>
            <div>
              <b>3</b>
              <span><ContentText name="main.009" /></span>
            </div>
            <div>
              <b><ContentText name="main.010" /></b>
              <span><ContentText name="main.011" /></span>
            </div>
          </div>
          <span className="hero-disclaimer"><ContentText name="main.012" /></span>
        </section>
        <section className="situations">
          <h2><ContentText name="main.013" /></h2>
          <div className={"ticker " + (paused ? "paused" : "")}>
            <div>
              {[...Array(2)].map((_, i) => (
                <div className="ticker-copy" key={i} aria-hidden={i === 1}>
                  {[
                    t("cards.006"),
                    t("cards.007"),
                    t("cards.008"),
                    t("cards.009"),
                    t("cards.010"),
                    t("cards.011"),
                  ].map((t) => (
                    <span key={t}>{t}</span>
                  ))}
                </div>
              ))}
            </div>
          </div>
          <button
            className="pause"
            onClick={() => setPaused(!paused)}
            aria-pressed={paused}
          >
            {paused ? t("main.extra.170") : t("main.extra.171")}
          </button>
        </section>
        <section className="current">
          <h2><ContentText name="main.014" /></h2>
          <div className="current-grid">
            {[
              [
                t("cards.012"),
                t("cards.013"),
              ],
              [
                t("cards.014"),
                t("cards.015"),
              ],
              [
                t("cards.016"),
                t("cards.017"),
              ],
              [
                t("cards.018"),
                t("cards.019"),
              ],
            ].map(([h, p], i) => (
              <article key={h}>
                <span className="black-icon">0{i + 1}</span>
                <h3>{h}</h3>
                <p>{p}</p>
              </article>
            ))}
          </div>
        </section>
        <section className="solution">
          <span className="section-label"><ContentText name="main.015" /></span>
          <h2><ContentText name="main.016" /></h2>
          <p><ContentText name="main.017" /></p>
          <a href={content.links["link.5"] ?? "#how"} className="button"><ContentText name="main.extra.137" /><Icon />
          </a>
          <div className="solution-line">
            <span>Personal</span>
            <i />
            <span>QORGO X</span>
            <i />
            <span>Control</span>
          </div>
        </section>
        <section className="how" id="how">
          <h2><ContentText name="main.018" /></h2>
          <div className="how-grid">
            {[
              [
                t("cards.020"),
                t("cards.021"),
                "shield",
              ],
              [
                t("cards.022"),
                t("cards.023"),
                "pin",
              ],
              [
                t("cards.024"),
                t("cards.025"),
                "arrow",
              ],
              [
                t("cards.026"),
                t("cards.027"),
                "shield",
              ],
            ].map(([h, p, icon], i) => (
              <article key={h}>
                <span className="step-num">0{i + 1}</span>
                <div className="how-illustration">
                  <Icon name={icon} size={45} />
                </div>
                <h3>{h}</h3>
                <p>{p}</p>
              </article>
            ))}
          </div>
          <p className="section-note"><ContentText name="main.019" /></p>
        </section>
        <section className="response" id="response">
          <h2><ContentText name="main.020" /></h2>
          <div className="response-head">
            <h3><ContentText name="main.021" /></h3>
            <p><ContentText name="main.022" /></p>
          </div>
          <div className="response-grid">
            <div className="response-visual">
              <CityMap />
            </div>
            <div className="response-items">
              {[
                [
                  t("cards.028"),
                  t("cards.029"),
                ],
                [
                  t("cards.030"),
                  t("cards.031"),
                ],
                [
                  t("cards.032"),
                  t("cards.033"),
                ],
                [
                  t("cards.034"),
                  t("cards.035"),
                ],
              ].map(([h, p]) => (
                <article key={h}>
                  <Icon name="shield" />
                  <div>
                    <h3>{h}</h3>
                    <p>{p}</p>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>
        <section className="features" id="features">
          <h2><ContentText name="main.023" /></h2>
          <div className="features-grid">
            <article className="feature-card sos-feature">
              <div>
                <span className="black-icon">
                  <Icon name="shield" />
                </span>
                <h3><ContentText name="main.024" /></h3>
                <p><ContentText name="main.025" /></p>
              </div>
              <div className="feature-visual sos-visual">
                <div className="demo-rings">
                  <i />
                  <i />
                  <i />
                  <span>
                    <Icon name="shield" size={35} />
                  </span>
                </div>
                <Slider />
              </div>
            </article>
            <article className="feature-card location-feature">
              <div>
                <span className="black-icon">
                  <Icon name="pin" />
                </span>
                <h3><ContentText name="main.026" /></h3>
                <p><ContentText name="main.027" /></p>
              </div>
              <div className="feature-visual location-visual">
                <div className="route-line" />
                <span className="location-marker">
                  <Icon name="pin" size={30} />
                </span>
                <span className="origin-dot" />
              </div>
            </article>
            <article className="feature-card monitoring-feature">
              <div>
                <span className="black-icon">
                  <Icon name="shield" />
                </span>
                <h3><ContentText name="main.028" /></h3>
                <p><ContentText name="main.029" /></p>
              </div>
              <div className="feature-visual monitoring-visual">
                <div className="arrival">
                  <span>✓</span>
                  <b><ContentText name="main.030" /></b>
                  <small><ContentText name="main.031" /></small>
                </div>
                <span className="timer">
                  18:30<small><ContentText name="main.extra.138" /></small>
                </span>
              </div>
            </article>
            <article className="feature-card terminal-feature">
              <div>
                <span className="black-icon">
                  <Icon name="arrow" />
                </span>
                <h3>
                  Fake Call
                </h3>
                <p><ContentText name="main.extra.139" /></p>
              </div>
              <div className="feature-visual fake-call-visual" aria-hidden="true">
                <span className="fake-call-avatar"><ContentText name="main.extra.140" /></span>
                <b><ContentText name="main.extra.141" /></b>
                <span><ContentText name="main.extra.142" /></span>
                <div className="fake-call-actions"><span>✕</span><span>☎</span></div>
              </div>
            </article>
          </div>
          <p className="section-note"><ContentText name="main.extra.143" /></p>
        </section>
        <Pricing />
        <section className="pilot" id="pilot">
          <h2><ContentText name="main.extra.144" /></h2>
          <p className="section-subtitle"><ContentText name="main.extra.145" /><br /><ContentText name="main.extra.146" /></p>
          <div className="pilot-grid">
            <article>
              <span className="pill"><ContentText name="main.extra.147" /></span>
              <h3><ContentText name="main.extra.148" /><br /><ContentText name="main.extra.149" /></h3>
              <p><ContentText name="main.extra.150" /></p>
              <ul>
                <li><ContentText name="main.extra.151" /></li>
                <li><ContentText name="main.extra.152" /></li>
                <li><ContentText name="main.extra.153" /></li>
              </ul>
              <a href={content.links["link.6"] ?? "#partnership"} className="button"><ContentText name="main.extra.154" /><Icon />
              </a>
            </article>
            <article>
              <span className="pill"><ContentText name="main.extra.155" /></span>
              <h3><ContentText name="main.extra.156" /><br /><ContentText name="main.extra.157" /></h3>
              <p><ContentText name="main.extra.158" /></p>
              <ul>
                <li><ContentText name="main.extra.159" /></li>
                <li><ContentText name="main.extra.160" /></li>
                <li><ContentText name="main.extra.161" /></li>
              </ul>
              <a href={content.presentation_url} download className="button"><ContentText name="main.extra.162" /><Icon name="down" />
              </a>
            </article>
          </div>
        </section>
        <section className="family-banner">
          <div className="family-art" aria-hidden="true">
            <div className="family-circle circle-one" />
            <div className="family-circle circle-two" />
            <div className="family-symbol">
              <Icon name="shield" size={80} />
            </div>
            <span><ContentText name="main.032" /></span>
          </div>
          <div>
            <h2><ContentText name="main.033" /></h2>
            <p><ContentText name="main.034" /></p>
            <a href={content.links["link.7"] ?? "#partnership"} className="button"><ContentText name="main.extra.163" /><Icon />
            </a>
          </div>
        </section>
        <section className="faq" id="faq">
          <h2><ContentText name="main.035" /></h2>
          <div className="faq-list">
            {content.faqs.map(([q, a], i) => (
              <details key={q}>
                <summary>
                  <span className="faq-num">0{i + 1}</span>
                  <h3>{q}</h3>
                  <span className="faq-plus">+</span>
                </summary>
                <p>{a}</p>
              </details>
            ))}
          </div>
        </section>
        <section className="contact" id="partnership">
          <h2><ContentText name="main.036" /></h2>
          <p><ContentText name="main.037" /></p>
          <a
            className="button white-button"
            href={content.presentation_url}
            download
          >
            <Icon name="down" /><ContentText name="main.extra.164" /></a>
        </section>
      </main>
      {content.documents.length > 0 && <section className="faq" id="documents">
        <h2><ContentText name="main.documents" /></h2>
        <div className="faq-list">{content.documents.map(document => <details key={document.slug} id={document.slug}>
          <summary>{document.title}</summary><p style={{ whiteSpace: "pre-wrap" }}>{document.body}</p>
        </details>)}</div>
      </section>}
      <footer>
        <div>
          <a className="brand" href={content.links["link.8"] ?? "#"}>
            <img src="/brand/qorgo-dark.svg" alt="" />
            <span>qorgo</span>
          </a>
          <p><ContentText name="main.038" /></p>
        </div>
        <div>
          <b><ContentText name="main.039" /></b>
          <p><ContentText name="main.040" /></p>
        </div>
        <div>
          <a href={content.links["link.9"] ?? "#features"}><ContentText name="main.041" /></a>
          <a href={content.links["link.10"] ?? "#pilot"}><ContentText name="main.042" /></a>
          <a href={content.links["link.11"] ?? "#faq"}><ContentText name="main.043" /></a>
        </div>
        <div className="footer-bottom">
          <span>© 2026 QORGO</span>
          <a
            className="deo-credit"
            href="https://crm.deo-core.codes/ref/kj_fQUTwe6qMla9_"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Made by DEO — открыть сайт DEO в новой вкладке"
          >
            <img src="/brand/made-by-deo.png" alt="Made by DEO" width="632" height="128" loading="lazy" />
          </a>
          <a href={content.links["link.12"] ?? "#"}><ContentText name="main.044" /></a>
        </div>
      </footer>
    </>
  );
}
export function App() { return <ContentProvider><Landing /></ContentProvider>; }
if (typeof document !== "undefined") {
  const root = document.getElementById("root");
  if (root.hasChildNodes()) hydrateRoot(root, <App />);
  else createRoot(root).render(<App />);
}
