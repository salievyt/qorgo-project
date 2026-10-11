import React, { createContext, useContext, useEffect, useState } from "react";
import defaults from "./content-defaults.json";
const Context = createContext(null);
const endpoint = import.meta.env.VITE_CONTENT_API_URL || "https://api.qorgo.services/api/v1/content/";
export function ContentProvider({ children }) {
  const [content, setContent] = useState(defaults);
  useEffect(() => {
    const controller = new AbortController();
    fetch(endpoint, { signal: controller.signal, cache: "no-store" })
      .then(response => { if (!response.ok) throw new Error("Content unavailable"); return response.json(); })
      .then(data => {
        if (!data.texts || !Array.isArray(data.faqs) || !Array.isArray(data.pricing?.plans)) return;
        setContent({ ...defaults, ...data, texts: { ...defaults.texts, ...data.texts }, links: { ...defaults.links, ...data.links } });
      }).catch(() => {});
    return () => controller.abort();
  }, []);
  return <Context.Provider value={{ content, t: key => content.texts[key] ?? defaults.texts[key] ?? "" }}>{children}</Context.Provider>;
}
export function useContent() { return useContext(Context); }
export function ContentText({ name }) {
  const { t } = useContent();
  return t(name).split("\n").map((line, index) => <React.Fragment key={index}>{index > 0 && <br />}{line}</React.Fragment>);
}
