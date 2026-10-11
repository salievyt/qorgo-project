import React, { useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";
import { Pricing } from "./pricing.jsx";
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
          {done ? "Жест завершён" : "Потяните вправо"} <span>› › ›</span>
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
            <span>Это демо. Сигнал не отправлен.</span>
            <button
              onClick={() => {
                setDone(false);
                setValue(0);
              }}
            >
              Повторить
            </button>
          </>
        ) : (
          <span>Доведите круг до правого края. Неполный свайп отменяется.</span>
        )}
      </div>
    </div>
  );
}
function CityMap() {
  return (
    <div className="city-map">
      <svg className="map-svg" viewBox="0 0 660 600" aria-hidden="true">
        <rect width="660" height="600" fill="#e8e5dc" />
        <g fill="#d7d9c9">
          <path d="M0 70h148v125H0zM382 0h190v128H382zM445 390h215v210H445zM0 420h120v180H0z" />
        </g>
        <g fill="#dfddd4" stroke="#cccac0" strokeWidth="1">
          <path d="M182 32h127v90H182zM182 156h130v97H182zM345 167h137v102H345zM24 240h124v118H24zM184 287h130v116H184zM355 305h151v73H355zM185 440h119v135H185zM348 429h61v170H348zM550 171h111v184H550z" />
        </g>
        <path
          d="M-25 390C125 360 218 250 327 310S498 485 705 410"
          stroke="#bbcec6"
          strokeWidth="36"
          fill="none"
        />
        <g stroke="#faf8f1" fill="none">
          <path
            d="M164-40v700M326-40v700M523-40v700M-30 142h750M-30 273h750M-30 418h750"
            strokeWidth="17"
          />
          <path
            d="M-10 62h750M-10 215h750M-10 520h750M74-10v650M423-10v650M607-10v650"
            strokeWidth="6"
          />
        </g>
        <path
          d="m189 324 137-50 90-82 107-48"
          fill="none"
          stroke="#b03d32"
          strokeWidth="2.5"
          strokeDasharray="6 5"
        />
        <circle cx="189" cy="324" r="54" fill="#b03d3212" />
        <circle cx="189" cy="324" r="30" fill="#b03d321c" />
        <circle
          cx="189"
          cy="324"
          r="8"
          fill="#b03d32"
          stroke="#fff"
          strokeWidth="4"
        />
        <circle
          cx="523"
          cy="144"
          r="6"
          fill="#333f35"
          stroke="#fff"
          strokeWidth="3"
        />
        <g fontFamily="Arial" fontSize="9" fill="#8e9386" letterSpacing="1.5">
          <text x="41" y="126">
            ПАРК
          </text>
          <text x="413" y="76">
            УНИВЕРСИТЕТ
          </text>
          <text x="464" y="556">
            ЖИЛОЙ КВАРТАЛ
          </text>
        </g>
      </svg>
      <div className="map-top">
        <span>
          <i /> Сценарий реагирования
        </span>
        <span>Демонстрация</span>
      </div>
      <div className="map-signal">
        <span className="signal-dot" />
        <div>
          <b>Получен сигнал SOS</b>
          <small>Местоположение определено</small>
        </div>
        <span className="signal-time">сейчас</span>
      </div>
      <div className="map-control">
        <Icon name="shield" />
        <span>Диспетчерская</span>
      </div>
      <div className="map-bottom">
        <span>Человек → Сигнал → Координация</span>
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
          <span>Концепт приложения</span>
        </div>
        <div className="personal-head">
          <span>Круг безопасности</span>
          <h3>
            Быть рядом.
            <br />
            Даже на расстоянии.
          </h3>
        </div>
        <div className="family-row">
          <span className="avatar">А</span>
          <span className="avatar">М</span>
          <span>Ваши доверенные контакты</span>
          <Icon size={16} />
        </div>
        <div className="try-label">ПОПРОБУЙТЕ ЖЕСТ SOS</div>
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
          <span>ГОЛОСОВАЯ СВЯЗЬ</span>
        </div>
        <div className="terminal mini">
          <b>
            QORGO <small>X MINI</small>
          </b>
          <div className="physical-sos">SOS</div>
          <span>ТРЕВОЖНЫЙ СИГНАЛ</span>
        </div>
        <p>Схематичный концепт. Финальный корпус в разработке.</p>
      </div>
    );
  return (
    <div className="control-preview">
      <div className="preview-heading">
        <b>QORGO Control</b>
        <span>Концепт панели</span>
      </div>
      <div className="control-alert">
        <span className="signal-dot" /> Сигнал SOS <span>Новый</span>
      </div>
      <dl>
        <div>
          <dt>Источник</dt>
          <dd>Терминал X LITE</dd>
        </div>
        <div>
          <dt>Место</dt>
          <dd>Площадка пилота</dd>
        </div>
        <div>
          <dt>Состояние</dt>
          <dd>Ожидает обработки</dd>
        </div>
      </dl>
      <div className="incident-route">
        <i />
        <span>Сигнал получен</span>
        <i />
        <span>Координация помощи</span>
      </div>
      <p>Демонстрационные данные</p>
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
        QORGO<span>Ваш круг безопасности</span>
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
const faqs = [
  [
    "Как работает QORGO?",
    "В предполагаемом сценарии полный свайп SOS активирует тревогу. Местоположение и уведомление передаются доверенным контактам, а для городских терминалов — в диспетчерскую платформу.",
  ],
  [
    "Можно ли уже скачать приложение?",
    "Проект находится на стадии концепции и подготовки требований. На сайте показаны демонстрационные интерфейсы; действующее приложение пока не представлено.",
  ],
  [
    "Кто будет реагировать на SOS?",
    "В приложении предполагается уведомление доверенных контактов. Для терминалов необходимо согласовать партнёра по диспетчеризации и реагированию на этапе пилота.",
  ],
  [
    "Когда и где планируется пилот?",
    "Предлагаемая территория — Ош. Даты, площадка и порядок реагирования предстоит согласовать с партнёрами.",
  ],
  [
    "Есть ли сотрудничество с государством?",
    "Действующие государственные партнёрства и интеграции пока не заявлены. В перспективе QORGO планируется предложить государственным и муниципальным организациям.",
  ],
  [
    "Что происходит при свайпе на сайте?",
    "Это локальная демонстрация. Реальный сигнал не отправляется, геолокация не запрашивается. Неполный свайп возвращает круг в начало.",
  ],
];
function App() {
  const [menu, setMenu] = useState(false),
    [paused, setPaused] = useState(false);
  return (
    <>
      <a className="skip-link" href="#main">
        Перейти к содержанию
      </a>
      <header>
        <a className="brand" href="#">
          <img src="/brand/qorgo-dark.svg" alt="" />
          <span>qorgo</span>
        </a>
        <nav className={menu ? "open" : ""} aria-label="Основная навигация">
          {[
            ["#how", "Как работает"],
            ["#response", "Кто поможет"],
            ["#features", "Возможности"],
            ["#pricing", "Тарифы"],
            ["#pilot", "Пилот"],
            ["#faq", "FAQ"],
          ].map(([href, name]) => (
            <a href={href} key={href} onClick={() => setMenu(false)}>
              {name}
            </a>
          ))}
        </nav>
        <a href="#partnership" className="button header-cta">
          <Icon name="down" size={16} /> О проекте
        </a>
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
            <h1>
              Будьте спокойнее
              <br />
              за тех, кто
              <br />
              вам дорог.
            </h1>
            <p>
              QORGO объединяет личную и городскую безопасность. <br />
              Один SOS-сигнал — первый шаг к помощи.
            </p>
            <a className="button" href="#features">
              Познакомиться с QORGO <Icon />
            </a>
          </div>
          <div className="floating-note note-one">
            <span className="note-avatar">
              <Icon name="shield" />
            </span>
            <div>
              <b>Круг безопасности</b>
              <small>Близкие получают уведомление</small>
            </div>
          </div>
          <div className="floating-note note-two">
            <span className="note-avatar alert-avatar">
              <Icon name="pin" />
            </span>
            <div>
              <b>Сигнал SOS</b>
              <small>Местоположение передано</small>
            </div>
          </div>
          <Phone />
          <div className="hero-facts">
            <div>
              <b>1</b>
              <span>
                полный свайп
                <br />
                для активации SOS
              </span>
            </div>
            <div>
              <b>3</b>
              <span>
                направления:
                <br />
                Personal, X и Control
              </span>
            </div>
            <div>
              <b>Ош</b>
              <span>
                предлагаемый город
                <br />
                пилотного проекта
              </span>
            </div>
          </div>
          <span className="hero-disclaimer">
            Концепция проекта · Демонстрация интерфейса
          </span>
        </section>
        <section className="situations">
          <h2>Когда особенно важна связь?</h2>
          <div className={"ticker " + (paused ? "paused" : "")}>
            <div>
              {[...Array(2)].map((_, i) => (
                <div className="ticker-copy" key={i} aria-hidden={i === 1}>
                  {[
                    "Возвращение домой вечером",
                    "Незнакомое место",
                    "Ребёнок задержался",
                    "Человек потерялся",
                    "Нужна помощь на улице",
                    "Нет возможности позвонить",
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
            {paused ? "Продолжить движение" : "Приостановить движение"}
          </button>
        </section>
        <section className="current">
          <h2>
            Почему одной связи
            <br />
            бывает недостаточно?
          </h2>
          <div className="current-grid">
            {[
              [
                "Позвонить близким",
                "Не всегда получается объяснить, что произошло и где вы находитесь.",
              ],
              [
                "Отправить сообщение",
                "В тревожной ситуации трудно набирать текст и ждать ответа.",
              ],
              [
                "Поделиться точкой",
                "Местоположение полезно, но важно, чтобы нужные люди получили и сам сигнал.",
              ],
              [
                "Попросить помощи рядом",
                "На улице не всегда есть человек, к которому можно обратиться.",
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
          <span className="section-label">НАША КОНЦЕПЦИЯ</span>
          <h2>
            QORGO — безопасность
            <br />
            человека, семьи и города.
          </h2>
          <p>
            Приложение для близких, SOS-терминалы для общественных мест
            <br />и платформа координации помощи — в одной экосистеме.
          </p>
          <a href="#how" className="button">
            Как это устроено <Icon />
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
          <h2>Как работает?</h2>
          <div className="how-grid">
            {[
              [
                "Полный свайп SOS",
                "Проведите ползунок до правого края. Неполное движение отменяет активацию.",
                "shield",
              ],
              [
                "Передача информации",
                "Сигнал содержит местоположение, чтобы получатели понимали, где нужна помощь.",
                "pin",
              ],
              [
                "Уведомление близких",
                "Выбранные доверенные контакты получают тревожное уведомление.",
                "arrow",
              ],
              [
                "Координация ответа",
                "Для терминалов сигнал предполагается передавать в QORGO Control.",
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
          <p className="section-note">
            Предполагаемый сценарий. Порядок реагирования уточняется при
            подготовке пилота.
          </p>
        </section>
        <section className="response" id="response">
          <h2>Кто поможет?</h2>
          <div className="response-head">
            <h3>
              Личная связь с близкими.
              <br />
              Городская — с партнёрами.
            </h3>
            <p>
              QORGO проектируется как связующее звено.
              <br />У каждого сценария — свой круг получателей.
            </p>
          </div>
          <div className="response-grid">
            <div className="response-visual">
              <CityMap />
            </div>
            <div className="response-items">
              {[
                [
                  "Доверенные контакты",
                  "Люди, которых пользователь выбирает сам: семья, друзья и близкие.",
                ],
                [
                  "Партнёр по реагированию",
                  "Для городского пилота необходима организация, принимающая и обрабатывающая SOS-сигналы.",
                ],
                [
                  "Диспетчерская платформа",
                  "Control предполагает карту событий и управление инцидентами.",
                ],
                [
                  "Проверка на практике",
                  "Скорость ответа и надёжность нужно измерить в ходе пилота.",
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
          <h2>Возможности</h2>
          <div className="features-grid">
            <article className="feature-card sos-feature">
              <div>
                <span className="black-icon">
                  <Icon name="shield" />
                </span>
                <h3>Кнопка SOS</h3>
                <p>
                  Полный свайп передаёт сигнал SOS, координаты и данные профиля
                  для вызова охраны в зоне обслуживания.
                </p>
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
                <h3>
                  Локация
                  <br />
                  близких
                </h3>
                <p>
                  Местоположение близких в реальном времени — с их согласия,
                  чтобы знать, где они находятся.
                </p>
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
                <h3>
                  Мониторинг
                  <br />близких
                </h3>
                <p>
                  Уведомления, когда близкий приходит в выбранное место
                  или покидает его: домой, в школу или на работу.
                </p>
              </div>
              <div className="feature-visual monitoring-visual">
                <div className="arrival">
                  <span>✓</span>
                  <b>Прибытие домой</b>
                  <small>Пример уведомления</small>
                </div>
                <span className="timer">
                  18:30<small>Время прибытия</small>
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
                <p>
                  Виртуальный входящий звонок — повод завершить неприятную
                  встречу или выйти из неловкой ситуации.
                </p>
              </div>
              <div className="feature-visual fake-call-visual" aria-hidden="true">
                <span className="fake-call-avatar">М</span>
                <b>Мама</b>
                <span>Входящий звонок · демонстрация</span>
                <div className="fake-call-actions"><span>✕</span><span>☎</span></div>
              </div>
            </article>
          </div>
          <p className="section-note">
            Эти четыре функции входят в утверждённый состав QORGO и готовятся к запуску.
            Вызов охраны будет доступен в тарифе с реагированием после подключения партнёра.
            Целевое время прибытия — 3–7 минут; фактические сроки и зона покрытия будут подтверждены в пилоте.
          </p>
        </section>
        <Pricing />
        <section className="pilot" id="pilot">
          <h2>Начнём с пилота в Оше</h2>
          <p className="section-subtitle">
            Сначала проверить сценарий на ограниченной площадке.
            <br />
            Затем принимать решение о масштабировании.
          </p>
          <div className="pilot-grid">
            <article>
              <span className="pill">Подготовка</span>
              <h3>
                Площадка
                <br />и партнёр
              </h3>
              <p>
                Согласовать территорию, места установки и порядок приёма
                тревожных сигналов.
              </p>
              <ul>
                <li>Площадка внедрения</li>
                <li>Партнёр по реагированию</li>
                <li>Критерии оценки</li>
              </ul>
              <a href="#partnership" className="button">
                О программе пилота <Icon />
              </a>
            </article>
            <article>
              <span className="pill">Испытания</span>
              <h3>
                Прототипы
                <br />и сценарии
              </h3>
              <p>
                Проверить полный путь тревоги, связь, питание и работу с ложными
                активациями.
              </p>
              <ul>
                <li>Устройства LITE и MINI</li>
                <li>Доставка SOS-сигнала</li>
                <li>Результаты испытаний</li>
              </ul>
              <a href="/QORGO_Presentation.pptx" download className="button">
                Скачать презентацию <Icon name="down" />
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
            <span>Человек · Семья · Город</span>
          </div>
          <div>
            <h2>
              Технологии безопасности
              <br />
              начинаются с людей.
            </h2>
            <p>
              Мы готовим концепцию QORGO для обсуждения с площадками,
              муниципалитетами и партнёрами по безопасности.
            </p>
            <a href="#partnership" className="button">
              Узнать о проекте <Icon />
            </a>
          </div>
        </section>
        <section className="faq" id="faq">
          <h2>Частые вопросы</h2>
          <div className="faq-list">
            {faqs.map(([q, a], i) => (
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
          <h2>
            Начнём разговор
            <br />о безопасности.
          </h2>
          <p>
            Презентация QORGO и предложенного пилота —<br />
            для потенциальных партнёров проекта.
          </p>
          <a
            className="button white-button"
            href="/QORGO_Presentation.pptx"
            download
          >
            <Icon name="down" /> Скачать презентацию QORGO
          </a>
        </section>
      </main>
      <footer>
        <div>
          <a className="brand" href="#">
            <img src="/brand/qorgo-dark.svg" alt="" />
            <span>qorgo</span>
          </a>
          <p>Проект DEO-CORE</p>
        </div>
        <div>
          <b>Личная и городская безопасность</b>
          <p>
            Концепция и подготовка требований.
            <br />
            Государственные партнёрства пока не заявлены.
          </p>
        </div>
        <div>
          <a href="#features">Возможности</a>
          <a href="#pilot">Пилотный проект</a>
          <a href="#faq">Частые вопросы</a>
        </div>
        <div className="footer-bottom">
          <span>© 2026 QORGO</span>
          <a href="#">Наверх ↑</a>
        </div>
      </footer>
    </>
  );
}
createRoot(document.getElementById("root")).render(<App />);
