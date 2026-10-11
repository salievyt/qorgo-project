import React, { useState } from "react";
import { ContentText, useContent } from "./content.jsx";
const money = (value) => new Intl.NumberFormat("ru-RU").format(value);
export function Pricing() {
  const { content, t } = useContent();
  const catalog = content.pricing;
  const [annual, setAnnual] = useState(false);
  return (
    <section className="pricing" id="pricing" aria-labelledby="pricing-title">
      <span className="pill"><ContentText name="pricing.001" /></span>
      <h2 id="pricing-title"><ContentText name="pricing.002" /></h2>
      <p className="section-subtitle"><ContentText name="pricing.003" /></p>
      <p className="section-note">{catalog.notice}</p>
      <div className="pricing-period" role="group" aria-label="Период подписки">
        <button type="button" aria-pressed={!annual} onClick={() => setAnnual(false)}><ContentText name="pricing.extra.165" /></button>
        <button type="button" aria-pressed={annual} onClick={() => setAnnual(true)}><ContentText name="pricing.extra.166" /></button>
      </div>
      <div className="pricing-grid">
        {catalog.plans.map((plan) => (
          <article key={plan.id} className={`pricing-card ${plan.id === "family" ? "pricing-family" : ""}`}>
            <span className="pill">{plan.id === "free" ? t("pricing.extra.173") : t("pricing.extra.174")}</span>
            <h3>{plan.name}</h3>
            <p>{plan.audience}</p>
            <div className="pricing-price" aria-live="polite"><strong>{money(annual ? plan.annual : plan.monthly)}</strong>{" "}<ContentText name="pricing.extra.167" /><span>/{annual && plan.annual ? t("pricing.extra.175") : t("pricing.extra.176")}</span></div>
            <p className="pricing-equivalent">{annual && plan.annual ? `≈ ${money(Math.round(plan.annual / 12))} ${t("pricing.annual_equivalent")}` : plan.monthly ? t("pricing.extra.177") : t("pricing.extra.178")}</p>
            {plan.features.length > 0 && <><h4><ContentText name="pricing.004" /></h4><ul>{plan.features.map((feature) => <li key={feature}>{feature}</li>)}</ul></>}
            <h4><ContentText name="pricing.005" /></h4>
            <ul>{plan.planned.map((feature) => <li key={feature}>{feature}</li>)}</ul>
            <p className="pricing-status">{plan.id === "free" ? t("pricing.extra.179") : t("pricing.extra.180")}</p>
          </article>
        ))}
      </div>
      <article className="pricing-response" aria-labelledby="response-plan-title">
        <div>
          <span className="pill"><ContentText name="pricing.006" /></span>
          <h3 id="response-plan-title"><ContentText name="pricing.007" /></h3>
          <p><ContentText name="pricing.008" /></p>
          <h4><ContentText name="pricing.009" /></h4>
          <ul>
            <li><ContentText name="pricing.010" /></li>
            <li><ContentText name="pricing.011" /></li>
            <li><ContentText name="pricing.012" /></li>
          </ul>
        </div>
        <div className="pricing-response-terms">
          <h4><ContentText name="pricing.013" /></h4>
          <p><ContentText name="pricing.014" /></p>
          <p className="pricing-status"><ContentText name="pricing.015" /></p>
        </div>
      </article>
      <p className="section-note"><ContentText name="pricing.016" /></p>
      <p className="section-note"><ContentText name="pricing.017" /></p>
      <p className="section-note"><ContentText name="pricing.018" /></p>
    </section>
  );
}
