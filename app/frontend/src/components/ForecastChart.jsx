import React, { useMemo } from 'react';
import Plot from 'react-plotly.js';
import moment from 'moment';

const ForecastChart = ({ historicalData, forecastData, symbol }) => {
  const chartData = useMemo(() => {
    if (!historicalData || historicalData.length === 0) {
      return { data: [], layout: {} };
    }

    // Prepare historical candlestick data
    const historicalCandles = historicalData
      .slice()
      .reverse() // Reverse to show chronological order
      .map(item => ({
        x: moment(item.Date).toDate(),
        open: item.Open || item.Close,
        high: item.High || item.Close,
        low: item.Low || item.Close,
        close: item.Close,
      }));

    // Prepare forecast data
    let forecastPoints = [];
    if (forecastData && forecastData.predictions) {
      forecastPoints = forecastData.predictions.map(pred => ({
        x: moment(pred.timestamp).toDate(),
        y: pred.value
      }));
    }

    // Candlestick trace for historical data
    const candlestickTrace = {
      x: historicalCandles.map(d => d.x),
      open: historicalCandles.map(d => d.open),
      high: historicalCandles.map(d => d.high),
      low: historicalCandles.map(d => d.low),
      close: historicalCandles.map(d => d.close),
      type: 'candlestick',
      name: '📊 Historical Prices',
      increasing: {
        line: { color: '#4caf50' }, // Green for bullish
        fillcolor: '#4caf50'
      },
      decreasing: {
        line: { color: '#f44336' }, // Red for bearish
        fillcolor: '#f44336'
      },
      hoverinfo: 'x+y',
      hovertemplate: 
        '<b>%{x}</b><br>' +
        'Open: $%{open}<br>' +
        'High: $%{high}<br>' +
        'Low: $%{low}<br>' +
        'Close: $%{close}<br>' +
        '<extra></extra>'
    };

    // Forecast line trace
    const forecastTrace = {
      x: forecastPoints.map(d => d.x),
      y: forecastPoints.map(d => d.y),
      type: 'scatter',
      mode: 'lines+markers',
      name: `🚀 AI Forecast (${forecastData?.model_used || 'Ensemble'})`,
      line: {
        color: '#ffeb3b', // Gold/Neon Yellow
        width: 3,
        dash: 'dot' // Dotted line
      },
      marker: {
        color: '#ffeb3b',
        size: 4,
        opacity: 0.8
      },
      opacity: 0.8,
      hoverinfo: 'x+y',
      hovertemplate: 
        '<b>%{x}</b><br>' +
        'Predicted: $%{y:.4f}<br>' +
        '🔮 AI Forecast<br>' +
        '<extra></extra>'
    };

    return {
      data: [candlestickTrace, ...(forecastPoints.length > 0 ? [forecastTrace] : [])],
      layout: {
        title: {
          text: `${symbol} — Real-Time Forecast Analysis`,
          font: { color: '#E0E0E0', size: 20 },
          x: 0.5
        },
        paper_bgcolor: '#000000', // Black background
        plot_bgcolor: '#000000',
        xaxis: {
          title: 'Time',
          color: '#AAA',
          showgrid: true,
          gridcolor: '#333333',
          type: 'date',
          tickformat: '%b %d, %H:%M',
          tickfont: { color: '#AAA', size: 12 },
          titlefont: { color: '#AAA', size: 14 }
        },
        yaxis: {
          title: 'Price (USD)',
          color: '#AAA',
          showgrid: true,
          gridcolor: '#333333',
          tickformat: '$.2f',
          tickfont: { color: '#AAA', size: 12 },
          titlefont: { color: '#AAA', size: 14 }
        },
        legend: {
          orientation: 'h',
          x: 0.3,
          y: 1.05,
          font: { color: '#DDD', size: 12 },
          bgcolor: 'rgba(0,0,0,0.8)',
          bordercolor: '#333333',
          borderwidth: 1
        },
        hovermode: 'x unified',
        showlegend: true,
        margin: {
          t: 80,
          b: 60,
          l: 80,
          r: 60
        }
      },
      config: {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false,
        toImageButtonOptions: {
          format: 'png',
          filename: `${symbol}_forecast_chart`,
          height: 600,
          width: 1200,
          scale: 1
        }
      }
    };
  }, [historicalData, forecastData, symbol]);

  if (!chartData || chartData.data.length === 0) {
    return (
      <div style={{ 
        height: '70vh',
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: '#000000',
        color: '#666666',
        fontSize: '18px',
        fontWeight: 'bold'
      }}>
        📊 No data available for chart
      </div>
    );
  }

  return (
    <div style={{ 
      height: '70vh',
      width: '100%',
      backgroundColor: '#000000'
    }}>
      <Plot
        data={chartData.data}
        layout={chartData.layout}
        config={chartData.config}
        style={{ width: '100%', height: '100%' }}
        useResizeHandler={true}
      />
    </div>
  );
};

export default ForecastChart;