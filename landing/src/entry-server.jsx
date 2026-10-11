import React from 'react';
import { renderToString } from 'react-dom/server';
import { App } from './main.jsx';
export function render() { return renderToString(<App />); }
