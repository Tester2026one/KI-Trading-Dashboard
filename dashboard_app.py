# dashboard_app.py
"""
Dashboard für Streamlit Community Cloud.
Kopie von monitoring/dashboard.py – optimiert für Cloud-Deployment.
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime


def load_backtest_results():
    """Lädt die neuesten Backtest-Ergebnisse."""
    results_path = Path("results/latest_backtest.json")
    if results_path.exists():
        with open(results_path, "r") as f:
            return json.load(f)
    return None


def main():
    st.set_page_config(
        page_title="KI Trading Dashboard",
        page_icon="📈",
        layout="wide",
    )

    st.title("📈 KI Trading System Dashboard")
    st.caption(f"Stand: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    data = load_backtest_results()

    if data is None:
        st.warning("Keine Backtest-Daten gefunden. Führe zuerst `python run_ensemble_backtest.py` aus.")
        st.info(
            "**So startest du:**\n"
            "1. Führe `python run_ensemble_backtest.py` aus\n"
            "2. Lade diese Seite neu (F5)\n\n"
            "**Cloud-Status:** Dashboard läuft 24/7 ✅"
        )
        return

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("🎯 Win-Rate", f"{data['win_rate_pct']:.1f}%")
    with col2:
        st.metric("💰 Rendite", f"{data['total_return_pct']:+.2f}%")
    with col3:
        st.metric("📊 Sharpe Ratio", f"{data['sharpe_ratio']:.2f}")
    with col4:
        st.metric("📉 Max Drawdown", f"{data['max_drawdown_pct']:.2f}%", delta_color="inverse")
    with col5:
        st.metric("🔢 Trades", f"{data['num_trades']}")

    st.divider()

    st.subheader("📊 Equity-Kurve")
    equity = data.get("equity_curve", [])
    if len(equity) > 0:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=equity,
            mode="lines",
            name="Kapital",
            line=dict(color="#00ff88", width=2),
            fill="tozeroy",
            fillcolor="rgba(0,255,136,0.1)",
        ))
        fig.add_hline(y=100000, line_dash="dash", line_color="gray")
        fig.update_layout(height=400, template="plotly_dark", margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

    trades = data.get("trades", [])
    if len(trades) > 0:
        st.subheader("📋 Letzte Trades")
        trades_df = pd.DataFrame(trades)
        display_df = trades_df.copy()
        if "pnl_pct" in display_df.columns:
            display_df["PnL %"] = display_df["pnl_pct"].apply(lambda x: f"{x:+.2f}%")
        if "type" in display_df.columns:
            display_df["Typ"] = display_df["type"].str.upper()
        if "exit_reason" in display_df.columns:
            display_df["Ausstieg"] = display_df["exit_reason"].str.replace("_", " ").str.title()
        cols_to_show = [c for c in ["Typ", "PnL %", "Ausstieg"] if c in display_df.columns]
        st.dataframe(display_df[cols_to_show].tail(20), use_container_width=True, hide_index=True)

        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("🥧 Ausstiegsgründe")
            exit_data = data.get("exit_reasons", {})
            if exit_data:
                exit_df = pd.DataFrame({"Grund": list(exit_data.keys()), "Anzahl": list(exit_data.values())})
                fig_pie = px.pie(exit_df, values="Anzahl", names="Grund", color_discrete_sequence=["#00ff88", "#ff4444", "#ffaa00"])
                fig_pie.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig_pie, use_container_width=True)

        with col_right:
            st.subheader("📈 PnL-Verteilung")
            if "pnl_pct" in trades_df.columns:
                fig_hist = px.histogram(trades_df, x="pnl_pct", nbins=30, color_discrete_sequence=["#00ff88"])
                fig_hist.add_vline(x=0, line_dash="dash", line_color="red")
                fig_hist.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig_hist, use_container_width=True)

    st.divider()
    st.caption(f"🤖 KI Intraday Trading System | Cloud-Version | Letzter Backtest: {data.get('timestamp', 'unbekannt')}")


if __name__ == "__main__":
    main()