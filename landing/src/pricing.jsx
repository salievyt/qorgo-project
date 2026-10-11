import React, { useState } from "react";
import catalog from "../../mobile/assets/tariffs.json";
const money = (value) => new Intl.NumberFormat("ru-RU").format(value);
export function Pricing() {
  const [annual, setAnnual] = useState(false);
  return (
    <section className="pricing" id="pricing" aria-labelledby="pricing-title">
      <span className="pill">Тарифы QORGO · сом</span>
      <h2 id="pricing-title">Помощь близких.<br />Больше возможностей для семьи.</h2>
      <p className="section-subtitle">SOS и связь с близкими — бесплатно. Premium и Семейный расширяют возможности приложения.</p>
      <p className="section-note">{catalog.notice}</p>
      <div className="pricing-period" role="group" aria-label="Период подписки">
        <button type="button" aria-pressed={!annual} onClick={() => setAnnual(false)}>Месяц</button>
        <button type="button" aria-pressed={annual} onClick={() => setAnnual(true)}>Год · экономия 17%</button>
      </div>
      <div className="pricing-grid">
        {catalog.plans.map((plan) => (
          <article key={plan.id} className={`pricing-card ${plan.id === "family" ? "pricing-family" : ""}`}>
            <span className="pill">{plan.id === "free" ? "Базовый доступ" : "Цифровой тариф · планируется"}</span>
            <h3>{plan.name}</h3>
            <p>{plan.audience}</p>
            <div className="pricing-price" aria-live="polite"><strong>{money(annual ? plan.annual : plan.monthly)}</strong> сом<span>/{annual && plan.annual ? "год" : "месяц"}</span></div>
            <p className="pricing-equivalent">{annual && plan.annual ? `≈ ${money(Math.round(plan.annual / 12))} сом/месяц · оплата за год целиком` : plan.monthly ? "При оплате за месяц" : "Без подписки"}</p>
            {plan.features.length > 0 && <><h4>В тестовой версии</h4><ul>{plan.features.map((feature) => <li key={feature}>{feature}</li>)}</ul></>}
            <h4>Планируется к запуску</h4>
            <ul>{plan.planned.map((feature) => <li key={feature}>{feature}</li>)}</ul>
            <p className="pricing-status">{plan.id === "free" ? "Базовые функции доступны в тестовой версии приложения" : "Подключение после запуска платных функций"}</p>
          </article>
        ))}
      </div>
      <article className="pricing-response" aria-labelledby="response-plan-title">
        <div>
          <span className="pill">Отдельный тариф · в разработке</span>
          <h3 id="response-plan-title">С реагированием</h3>
          <p>Для тех, кому нужна помощь охранного экипажа по сигналу SOS.</p>
          <h4>Планируемый состав</h4>
          <ul>
            <li>Передача SOS партнёру по реагированию</li>
            <li>Обработка тревоги диспетчером и выезд экипажа</li>
            <li>Статус вызова в приложении</li>
          </ul>
        </div>
        <div className="pricing-response-terms">
          <h4>Цена после согласования с партнёром</h4>
          <p>Тариф появится после согласования зоны покрытия, часов работы, стоимости и количества включённых выездов.</p>
          <p className="pricing-status">Пока недоступен для подключения</p>
        </div>
      </article>
      <p className="section-note">Выезд охраны и диспетчеризация не входят в тарифы за 199 и 349 сом. Услуга реагирования пока не запущена.</p>
      <p className="section-note">Автоматические SMS и устройства в подписку не входят. SMS из телефона — по тарифу вашего оператора.</p>
      <p className="section-note">AI-анализ и история за год — дальнейшие этапы развития. Реакция близких и служб не гарантируется подпиской.</p>
    </section>
  );
}
