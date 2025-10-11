// Trading Analytics Platform - Main JavaScript Application

// Global variables
let currentSymbol = 'IBM';
let priceChart = null;
let updateInterval = null;

// API Base URL
const API_BASE = 'http://localhost:8000/api';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadStockData(currentSymbol);
    
    // Auto-update every 30 seconds
    updateInterval = setInterval(() => {
        loadStockData(currentSymbol);
    }, 30000);
});

// Initialize application
function initializeApp() {
    // Setup chart
    const ctx = document.getElementById('priceChart').getContext('2d');
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Price',
                data: [],
                borderColor: '#4F46E5',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                borderWidth: 2,
                tension: 0.1
            }, {
                label: 'SMA 20',
                data: [],
                borderColor: '#10B981',
                borderWidth: 1,
                borderDash: [5, 5],
                tension: 0.1,
                backgroundColor: 'transparent'
            }, {
                label: 'SMA 50',
                data: [],
                borderColor: '#F59E0B',
                borderWidth: 1,
                borderDash: [5, 5],
                tension: 0.1,
                backgroundColor: 'transparent'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#9CA3AF'
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#9CA3AF'
                    }
                },
                y: {
                    position: 'right',
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#9CA3AF'
                    }
                }
            }
        }
    });
}

// Setup event listeners
function setupEventListeners() {
    // Symbol selector
    document.getElementById('symbolSelect').addEventListener('change', (e) => {
        currentSymbol = e.target.value;
        loadStockData(currentSymbol);
    });
    
    // Navigation tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            switchTab(e.target.dataset.tab);
        });
    });
    
    // Info buttons
    document.querySelectorAll('.info-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            showEducationalContent(e.target.dataset.topic);
        });
    });
    
    // Modal close button
    document.querySelector('.close').addEventListener('click', closeModal);
    
    // Close modal on outside click
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('educationModal');
        if (e.target === modal) {
            closeModal();
        }
    });
    
    // Time period buttons
    document.querySelectorAll('.time-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            // Load data for selected period
            loadStockData(currentSymbol);
        });
    });
}

// Load stock data
async function loadStockData(symbol) {
    try {
        // Show loading state
        showLoading();
        
        // Load overview data
        try {
            const overviewResponse = await fetch(`${API_BASE}/overview/${symbol}`);
            if (overviewResponse.ok) {
                const overviewData = await overviewResponse.json();
                updateOverview(overviewData);
            } else {
                console.error('Overview data not available');
            }
        } catch (e) {
            console.error('Error loading overview:', e);
        }
        
        // Load technical analysis
        try {
            const technicalResponse = await fetch(`${API_BASE}/technical/${symbol}`);
            if (technicalResponse.ok) {
                const technicalData = await technicalResponse.json();
                if (technicalData.indicators) {
                    updateTechnicalIndicators(technicalData.indicators);
                }
                if (technicalData.chart_data) {
                    updateChart(technicalData.chart_data);
                }
            } else {
                console.error('Technical data not available');
            }
        } catch (e) {
            console.error('Error loading technical:', e);
        }
        
        // Load signals
        try {
            const signalResponse = await fetch(`${API_BASE}/signals/${symbol}`);
            if (signalResponse.ok) {
                const signalData = await signalResponse.json();
                if (signalData.signal) {
                    updateSignals(signalData.signal);
                }
            }
        } catch (e) {
            console.error('Error loading signals:', e);
        }
        
        // Load AI Analysis if available
        try {
            const aiResponse = await fetch(`${API_BASE}/ai-analysis/${symbol}`);
            if (aiResponse.ok) {
                const aiData = await aiResponse.json();
                updateAIAnalysis(aiData);
            }
        } catch (e) {
            console.log('AI analysis not available');
        }
        
    } catch (error) {
        console.error('Error loading stock data:', error);
        showError('Failed to load stock data. Please try again.');
    } finally {
        hideLoading();
    }
}

// Update overview section
function updateOverview(data) {
    if (!data) return;
    
    // Update company info
    const companyName = document.querySelector('.company-name');
    if (companyName) companyName.textContent = data.name || data.symbol || 'IBM';
    
    const stockSymbol = document.querySelector('.stock-symbol');
    if (stockSymbol) stockSymbol.textContent = `${data.symbol || 'IBM'} • ${data.exchange || 'NYSE'}`;
    
    const logoCircle = document.querySelector('.logo-circle');
    if (logoCircle) logoCircle.textContent = data.symbol || 'IBM';
    
    // Update price info
    const priceInfo = data.current_price || {};
    const price = priceInfo.price || 0;
    const change = priceInfo.price_change || 0;
    const changePercent = priceInfo.price_change_percent || 0;
    
    const currentPriceElem = document.getElementById('currentPrice');
    if (currentPriceElem) currentPriceElem.textContent = `$${price.toFixed(2)}`;
    
    const priceChangeElem = document.getElementById('priceChange');
    if (priceChangeElem) {
        priceChangeElem.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}`;
        priceChangeElem.className = change >= 0 ? 'price-change positive' : 'price-change negative';
    }
    
    const changePercentElem = document.getElementById('priceChangePercent');
    if (changePercentElem) {
        changePercentElem.textContent = `${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%`;
        changePercentElem.className = change >= 0 ? 'price-change-percent positive' : 'price-change-percent negative';
    }
    
    const lastUpdateElem = document.getElementById('lastUpdate');
    if (lastUpdateElem) lastUpdateElem.textContent = new Date().toLocaleTimeString();
    
    // Update key stats
    const stats = data.key_stats || {};
    
    const marketCapElem = document.getElementById('marketCap');
    if (marketCapElem) marketCapElem.textContent = formatMarketCap(stats.market_cap);
    
    const peRatioElem = document.getElementById('peRatio');
    if (peRatioElem) peRatioElem.textContent = stats.pe_ratio ? stats.pe_ratio.toFixed(2) : 'N/A';
    
    const divYieldElem = document.getElementById('divYield');
    if (divYieldElem) divYieldElem.textContent = stats.dividend_yield ? `${(stats.dividend_yield * 100).toFixed(2)}%` : 'N/A';
    
    const range52wElem = document.getElementById('range52w');
    if (range52wElem) {
        range52wElem.textContent = stats['52_week_low'] && stats['52_week_high'] ? 
            `$${stats['52_week_low']} - $${stats['52_week_high']}` : 'N/A';
    }
}

// Update technical indicators
function updateTechnicalIndicators(indicators) {
    if (!indicators) return;
    
    // Update RSI
    const rsi = indicators.rsi || 50;
    document.getElementById('rsiValue').textContent = rsi.toFixed(2);
    document.getElementById('rsiFill').style.width = `${rsi}%`;
    
    let rsiStatus = 'Neutral';
    if (rsi > 70) rsiStatus = 'Overbought';
    else if (rsi < 30) rsiStatus = 'Oversold';
    document.getElementById('rsiStatus').textContent = rsiStatus;
    
    // Update MACD
    const macd = indicators.macd || {};
    document.getElementById('macdValue').textContent = (macd.macd || 0).toFixed(3);
    document.getElementById('signalValue').textContent = (macd.signal || 0).toFixed(3);
    document.getElementById('histogramValue').textContent = (macd.histogram || 0).toFixed(3);
    
    // Update Moving Averages
    const sma = indicators.sma || {};
    document.getElementById('sma20').textContent = sma.sma_20 ? `$${sma.sma_20.toFixed(2)}` : 'N/A';
    document.getElementById('sma50').textContent = sma.sma_50 ? `$${sma.sma_50.toFixed(2)}` : 'N/A';
    document.getElementById('sma200').textContent = sma.sma_200 ? `$${sma.sma_200.toFixed(2)}` : 'N/A';
    
    // Update Volume Analysis
    const volume = indicators.volume_analysis || {};
    document.getElementById('currentVolume').textContent = formatVolume(volume.current);
    document.getElementById('avgVolume').textContent = formatVolume(volume.avg_20);
    document.getElementById('volumeRatio').textContent = `${(volume.ratio || 1).toFixed(2)}x`;
    document.getElementById('volumeSignal').textContent = volume.interpretation || 'Normal volume';
    
    // Update Bollinger Bands
    const bollinger = indicators.bollinger_bands || {};
    document.getElementById('bbUpper').textContent = bollinger.upper ? `$${bollinger.upper.toFixed(2)}` : 'N/A';
    document.getElementById('bbMiddle').textContent = bollinger.middle ? `$${bollinger.middle.toFixed(2)}` : 'N/A';
    document.getElementById('bbLower').textContent = bollinger.lower ? `$${bollinger.lower.toFixed(2)}` : 'N/A';
    
    // Update Support & Resistance
    const sr = indicators.support_resistance || {};
    const resistance = sr.resistance || [];
    const support = sr.support || [];
    
    document.getElementById('resistanceLevels').innerHTML = resistance.length > 0 ?
        resistance.map(r => `$${r.toFixed(2)}`).join(' | ') : 'N/A';
    document.getElementById('supportLevels').innerHTML = support.length > 0 ?
        support.map(s => `$${s.toFixed(2)}`).join(' | ') : 'N/A';
    
    // Update Signal Strength
    const signalStrength = indicators.signal_strength || {};
    updateSignalStrength(signalStrength);
}

// Update chart
function updateChart(chartData) {
    if (!chartData || !priceChart) return;
    
    // Update chart data
    priceChart.data.labels = chartData.dates.slice(-100).map(date => {
        return new Date(date).toLocaleDateString();
    });
    
    priceChart.data.datasets[0].data = chartData.prices.slice(-100);
    
    if (chartData.sma_20) {
        priceChart.data.datasets[1].data = chartData.sma_20.slice(-100);
    }
    
    if (chartData.sma_50) {
        priceChart.data.datasets[2].data = chartData.sma_50.slice(-100);
    }
    
    priceChart.update();
}

// Update signals
function updateSignals(signal) {
    if (!signal) return;
    
    // Update signal action
    const actionElem = document.getElementById('signalAction');
    actionElem.textContent = signal.signal || 'HOLD';
    actionElem.className = 'signal-action';
    
    if (signal.signal.includes('BUY')) {
        actionElem.classList.add('buy');
    } else if (signal.signal.includes('SELL')) {
        actionElem.classList.add('sell');
    } else {
        actionElem.classList.add('hold');
    }
    
    // Update confidence
    document.getElementById('signalConfidence').textContent = `${(signal.confidence || 0).toFixed(1)}%`;
    
    // Update reasoning
    const reasonsList = document.getElementById('signalReasons');
    reasonsList.innerHTML = '';
    if (signal.reasoning && signal.reasoning.length > 0) {
        signal.reasoning.forEach(reason => {
            const li = document.createElement('li');
            li.textContent = reason;
            reasonsList.appendChild(li);
        });
    }
}

// Update signal strength indicator
function updateSignalStrength(signalStrength) {
    const strength = signalStrength.strength || 0;
    const action = signalStrength.action || 'HOLD';
    const signals = signalStrength.signals || [];
    
    // Update strength bar
    const fillElem = document.getElementById('strengthFill');
    const absStrength = Math.abs(strength);
    fillElem.style.width = `${absStrength}%`;
    fillElem.className = strength >= 0 ? 'strength-fill positive' : 'strength-fill negative';
    
    // Update strength value
    document.getElementById('strengthValue').textContent = strength.toFixed(1);
    
    // Update signal action
    const actionElem = document.getElementById('signalAction');
    actionElem.textContent = action;
    actionElem.className = 'signal-action';
    
    if (action.includes('BUY')) {
        actionElem.classList.add('buy');
    } else if (action.includes('SELL')) {
        actionElem.classList.add('sell');
    } else {
        actionElem.classList.add('hold');
    }
    
    // Update confidence
    document.getElementById('signalConfidence').textContent = `${(signalStrength.confidence || 0).toFixed(1)}%`;
    
    // Update signals list
    const signalsList = document.getElementById('signalReasons');
    signalsList.innerHTML = '';
    signals.forEach(signal => {
        const li = document.createElement('li');
        li.textContent = signal;
        signalsList.appendChild(li);
    });
}

// Switch between tabs
function switchTab(tabName) {
    // Update active tab
    document.querySelectorAll('.nav-tab').forEach(tab => {
        if (tab.dataset.tab === tabName) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Show/hide content
    document.querySelectorAll('.tab-content').forEach(content => {
        if (content.id === tabName) {
            content.style.display = 'block';
        } else {
            content.style.display = 'none';
        }
    });
}

// Show educational content
async function showEducationalContent(topic) {
    try {
        const response = await fetch(`${API_BASE}/education/${topic}`);
        const data = await response.json();
        
        const modal = document.getElementById('educationModal');
        document.getElementById('modalTitle').textContent = data.title;
        document.getElementById('modalDescription').textContent = data.description;
        
        // Create interpretation list
        const interpretDiv = document.getElementById('modalInterpretation');
        interpretDiv.innerHTML = '<h4>Interpretation:</h4><ul>';
        if (data.interpretation) {
            data.interpretation.forEach(item => {
                interpretDiv.innerHTML += `<li>${item}</li>`;
            });
        }
        interpretDiv.innerHTML += '</ul>';
        
        // Add usage info
        const usageDiv = document.getElementById('modalUsage');
        usageDiv.innerHTML = `<h4>How to Use:</h4><p>${data.usage}</p>`;
        
        modal.style.display = 'block';
    } catch (error) {
        console.error('Error loading educational content:', error);
    }
}

// Close modal
function closeModal() {
    document.getElementById('educationModal').style.display = 'none';
}

// Utility functions
function formatMarketCap(value) {
    if (!value) return 'N/A';
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toFixed(2)}`;
}

function formatVolume(value) {
    if (!value) return 'N/A';
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(0)}K`;
    return value.toString();
}

function showLoading() {
    // Add loading indicator
    document.body.classList.add('loading');
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.add('active');
}

function hideLoading() {
    // Remove loading indicator
    document.body.classList.remove('loading');
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.classList.remove('active');
}

function showError(message) {
    console.error(message);
    // You can add a toast notification here
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
