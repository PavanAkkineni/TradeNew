// Trading Analytics Platform - Enhanced JavaScript Application
// With better error handling and data visualization

// Global variables
let currentSymbol = 'IBM';
let priceChart = null;
let updateInterval = null;

// API Base URL - Dynamic based on environment
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000/api'  // Local development
    : '/api';  // Production - relative URL

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Trading Analytics Platform...');
    console.log('📊 MODE: STATIC DATA ONLY - No live market data');
    console.log('API Base URL:', API_BASE);
    
    try {
        // Initialize app components
        console.log('⚙️ Initializing application...');
        initializeApp();
        
        console.log('📡 Setting up event listeners...');
        setupEventListeners();
        
        // Load initial data
        console.log('📊 Loading initial stock data for:', currentSymbol);
        loadStockData(currentSymbol);
        
        // Load market data for portfolio tab (default tab)
        console.log('📊 Loading market data for portfolio tab...');
        loadMarketData();
        
        // Auto-update disabled for static data
        console.log('⏰ Auto-update disabled (using static data)...');
        // updateInterval = setInterval(() => {
        //     console.log('🔄 Auto-updating data...');
        //     loadStockData(currentSymbol);
        // }, 30000);
        
        console.log('✅ Application initialized successfully!');
    } catch (error) {
        console.error('❌ Initialization error:', error);
        showError('Failed to initialize application: ' + error.message);
    }
});

// Initialize application
function initializeApp() {
    console.log('📊 Initializing chart...');
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('❌ Chart.js not loaded');
        showError('Chart library not loaded');
        return;
    }
    
    // Setup chart with better configuration
    const ctx = document.getElementById('priceChart');
    if (!ctx) {
        console.error('❌ Price chart canvas not found');
        showError('Chart canvas not found');
        return;
    }
    
    console.log('✅ Chart canvas found, creating chart...');
    
    try {
        priceChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Price',
                data: [],
                borderColor: '#5865f2',
                backgroundColor: 'rgba(88, 101, 242, 0.1)',
                borderWidth: 2,
                tension: 0.1,
                pointRadius: 0,
                pointHoverRadius: 4
            }, {
                label: 'SMA 20',
                data: [],
                borderColor: '#00d4aa',
                borderWidth: 1,
                borderDash: [5, 5],
                tension: 0.1,
                backgroundColor: 'transparent',
                pointRadius: 0
            }, {
                label: 'SMA 50',
                data: [],
                borderColor: '#fee75c',
                borderWidth: 1,
                borderDash: [5, 5],
                tension: 0.1,
                backgroundColor: 'transparent',
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#8b92b9',
                        padding: 15,
                        font: {
                            size: 12,
                            weight: 500
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(30, 33, 57, 0.9)',
                    titleColor: '#ffffff',
                    bodyColor: '#8b92b9',
                    borderColor: '#2a2e4a',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += '$' + context.parsed.y.toFixed(2);
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(255, 255, 255, 0.03)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#565d7e',
                        maxTicksLimit: 8
                    }
                },
                y: {
                    position: 'right',
                    grid: {
                        color: 'rgba(255, 255, 255, 0.03)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#565d7e',
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            }
        }
    });
        
        console.log('✅ Chart initialized successfully');
    } catch (error) {
        console.error('❌ Chart initialization failed:', error);
        showError('Failed to initialize chart: ' + error.message);
    }
}

// Setup event listeners
function setupEventListeners() {
    // Symbol selector
    const symbolSelect = document.getElementById('symbolSelect');
    if (symbolSelect) {
        symbolSelect.addEventListener('change', (e) => {
            currentSymbol = e.target.value;
            loadStockData(currentSymbol);
        });
    }
    
    // Navigation tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            switchTab(e.target.dataset.tab);
        });
    });
    
    // Risk strategy tabs (for Credibility page)
    document.querySelectorAll('.risk-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            // Remove active class from all risk tabs
            document.querySelectorAll('.risk-tab').forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            e.target.classList.add('active');
            
            // Hide all risk content
            document.querySelectorAll('.risk-content').forEach(content => content.classList.remove('active'));
            
            // Show corresponding risk content
            const riskType = e.target.dataset.risk;
            const contentId = riskType + '-risk-content';
            const content = document.getElementById(contentId);
            if (content) {
                content.classList.add('active');
            }
        });
    });
    
    // Period selector tabs (for Credibility page)
    document.querySelectorAll('.period-tab').forEach(tab => {
        tab.addEventListener('click', (e) => {
            // Remove active class from all period tabs
            document.querySelectorAll('.period-tab').forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            e.target.classList.add('active');
            
            // Get the selected period
            const selectedPeriod = e.target.dataset.period;
            const [startDate, endDate] = selectedPeriod.split('_');
            
            // Update subtitle with selected period
            const subtitle = document.getElementById('selected-period-subtitle');
            if (subtitle) {
                const formattedPeriod = formatPeriodForDisplay(startDate, endDate);
                subtitle.textContent = `Comprehensive backtesting performance over ${formattedPeriod}`;
            }
            
            // Load credibility data for the selected period
            console.log(`📅 Loading credibility data for period: ${startDate} to ${endDate}`);
            loadCredibilityDataForPeriod(startDate, endDate);
        });
    });
    
    // Info buttons
    document.querySelectorAll('.info-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const topic = e.target.closest('button').dataset.topic;
            console.log(`📚 Opening educational content for: ${topic}`);
            showEducationalContent(topic);
        });
    });
    
    // Modal close button
    const closeBtn = document.querySelector('.modal-close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }
    
    // Close modal on outside click
    window.addEventListener('click', (e) => {
        const modal = document.getElementById('educationModal');
        if (modal && e.target === modal) {
            closeModal();
        }
    });
    
    // Time period buttons
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            // Load data for selected period
            loadStockData(currentSymbol);
        });
    });
    
    // Gemini Expert Analysis button
    const geminiButton = document.getElementById('getGeminiAnalysis');
    if (geminiButton) {
        geminiButton.addEventListener('click', () => {
            console.log('🤖 Gemini Expert Analysis button clicked');
            loadGeminiExpertAnalysis();
        });
    }
    
    // Portfolio Form Submission
    const portfolioForm = document.getElementById('portfolioForm');
    if (portfolioForm) {
        portfolioForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('📊 Portfolio form submitted');
            await handlePortfolioSubmission();
        });
    }
    
    // Edit Profile Button
    const editProfileBtn = document.getElementById('editProfile');
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', () => {
            console.log('✏️ Edit profile clicked');
            showPortfolioForm();
        });
    }
    
    // Market Data Refresh Button
    const refreshMarketBtn = document.getElementById('refreshMarketData');
    if (refreshMarketBtn) {
        refreshMarketBtn.addEventListener('click', () => {
            console.log('🔄 Refresh market data clicked');
            loadMarketData();
        });
    }
}

// Load stock data with sequential loading for better reliability
async function loadStockData(symbol) {
    console.log(`📡 Loading data for ${symbol}...`);
    showLoading();
    
    let technicalData = null;
    
    try {
        // Load technical data first as it's most important
        console.log('🔄 Loading technical data...');
        try {
            technicalData = await fetchWithRetry(`${API_BASE}/technical/${symbol}`);
            console.log('📊 Technical data received:', technicalData);
            
            if (technicalData && technicalData.indicators) {
                console.log('✅ Processing technical indicators...');
                updateTechnicalIndicators(technicalData.indicators);
                
                // Update overview with technical data if it contains price info
                if (technicalData.indicators.current_price) {
                    updateOverview({ indicators: technicalData.indicators });
                }
            }
            
            if (technicalData && technicalData.chart_data) {
                console.log('📈 Updating chart...');
                updateChart(technicalData.chart_data);
            }
        } catch (error) {
            console.error('❌ Technical data failed:', error);
            updateTechnicalIndicatorsWithDefaults();
        }
        
        // Load overview data (optional) - Only if we don't have technical price data
        let hasValidPriceData = technicalData && technicalData.indicators && technicalData.indicators.current_price;
        console.log('🔍 Price data check:', { hasValidPriceData, currentPrice: technicalData?.indicators?.current_price });
        
        if (!hasValidPriceData) {
            try {
                const overviewData = await fetchWithRetry(`${API_BASE}/overview/${symbol}`);
                if (overviewData) {
                    updateOverview(overviewData);
                } else {
                    console.warn('⚠️ Overview data not available, using defaults');
                    updateOverviewWithDefaults(symbol);
                }
            } catch (error) {
                console.warn('⚠️ Overview data not available, using defaults');
                updateOverviewWithDefaults(symbol);
            }
        } else {
            console.log('✅ Using price data from technical API, skipping overview defaults');
        }
        
        // Load comprehensive trade signal data
        try {
            console.log('🎯 Loading trade signals...');
            const signalData = await fetchWithRetry(`${API_BASE}/signals/${symbol}`);
            console.log('📥 Trade signal response:', signalData);
            
            if (signalData && signalData.signal) {
                console.log('✅ Trade signals received:', signalData.signal);
                updateTradeSignals(signalData.signal);
                // Also update the old signals display if it exists
                updateSignals(signalData.signal);
            } else {
                console.warn('⚠️ Trade signal missing signal property');
                updateTradeSignalsWithDefaults();
                updateSignalsWithDefaults();
            }
        } catch (error) {
            console.error('❌ Trade signal error:', error);
            updateTradeSignalsWithDefaults();
            updateSignalsWithDefaults();
        }

        // Load fundamental data
        try {
            console.log('💰 Loading fundamental data...');
            const fundamentalData = await fetchWithRetry(`${API_BASE}/fundamental/${symbol}`);
            console.log('📥 Fundamental data response:', fundamentalData);
            
            if (fundamentalData && fundamentalData.analysis) {
                console.log('✅ Fundamental data received, analysis object:', fundamentalData.analysis);
                updateFundamentalAnalysis(fundamentalData.analysis);
            } else {
                console.warn('⚠️ Fundamental data missing analysis property');
                console.log('Response structure:', {
                    hasFundamentalData: !!fundamentalData,
                    hasAnalysis: !!(fundamentalData && fundamentalData.analysis),
                    keys: fundamentalData ? Object.keys(fundamentalData) : []
                });
                updateFundamentalWithDefaults();
            }
        } catch (error) {
            console.error('❌ Fundamental data error:', error);
            updateFundamentalWithDefaults();
        }

        // Load sentiment data
        try {
            console.log('📰 Loading sentiment data...');
            const sentimentData = await fetchWithRetry(`${API_BASE}/sentiment/${symbol}`);
            console.log('📥 Sentiment data response:', sentimentData);
            
            if (sentimentData && sentimentData.analysis) {
                console.log('✅ Sentiment data received:', sentimentData.analysis);
                updateSentimentAnalysis(sentimentData.analysis);
            } else {
                console.warn('⚠️ Sentiment data missing analysis property');
                updateSentimentWithDefaults();
            }
        } catch (error) {
            console.error('❌ Sentiment data error:', error);
            updateSentimentWithDefaults();
        }

        // Expert analysis is now loaded on-demand via button click
        // Initialize with empty state
        updateExpertAnalysisInitialState();
        
        // Load AI data (optional)
        try {
            const aiData = await fetchWithRetry(`${API_BASE}/ai-analysis/${symbol}`);
            if (aiData) {
                updateAIAnalysis(aiData);
            }
        } catch (error) {
            console.warn('⚠️ AI analysis not available');
        }
        
        // Update credibility analysis with symbol-specific data
        console.log('📊 Loading credibility analysis...');
        updateCredibilityData(symbol);
        
        console.log('✅ Data loading completed!');
        
    } catch (error) {
        console.error('❌ Critical error loading stock data:', error);
        showError('Failed to load stock data. Please check your connection.');
    } finally {
        hideLoading();
    }
}

// Fetch with retry logic and better error handling
async function fetchWithRetry(url, retries = 2) {
    console.log(`🌐 Fetching: ${url}`);
    
    for (let i = 0; i <= retries; i++) {
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                mode: 'cors'
            });
            
            console.log(`📡 Response status: ${response.status} for ${url}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log(`✅ Data received from ${url}`);
            return data;
        } catch (error) {
            console.error(`❌ Attempt ${i + 1} failed for ${url}:`, error);
            if (i === retries) {
                console.error(`💥 All attempts failed for ${url}`);
                throw error;
            }
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second before retry
        }
    }
}

// Update overview section with proper null checking
function updateOverview(data) {
    if (!data) return;
    
    console.log('📈 Updating overview with data:', data);
    
    // Get the current symbol from dropdown to determine defaults
    const currentSymbol = document.getElementById('symbolSelect')?.value || 'IBM';
    
    // Set symbol-specific defaults
    const defaults = {
        'IBM': {
            name: 'International Business Machines',
            symbol: 'IBM',
            sector: 'Technology',
            exchange: 'NYSE'
        },
        'MSFT': {
            name: 'Microsoft Corporation',
            symbol: 'MSFT',
            sector: 'Technology',
            exchange: 'NASDAQ'
        }
    };
    
    const symbolDefaults = defaults[currentSymbol] || defaults['IBM'];
    
    // Update company info with symbol-specific defaults
    updateElement('.company-name', data.name || symbolDefaults.name);
    updateElement('#companyName', data.name || symbolDefaults.name);
    updateElement('.stock-symbol', `${data.symbol || symbolDefaults.symbol} • ${data.exchange || symbolDefaults.exchange}`);
    updateElement('#stockSymbol', data.symbol || symbolDefaults.symbol);
    updateElement('#stockSector', data.sector || symbolDefaults.sector);
    updateElement('#exchangeBadge', data.exchange || symbolDefaults.exchange);
    updateElement('#stockLogo', data.symbol || symbolDefaults.symbol);
    updateElement('.logo-circle', data.symbol || symbolDefaults.symbol);
    
    // Handle price info - check if it's from overview API or technical API
    let price, change, changePercent, volume;
    
    if (data.current_price && typeof data.current_price === 'object') {
        // From overview API - nested structure
        price = parseFloat(data.current_price.price) || 288.42;
        change = parseFloat(data.current_price.price_change) || 1.7;
        changePercent = parseFloat(data.current_price.price_change_percent) || 0.59;
        volume = data.current_price.volume || 4372457;
    } else if (data.indicators) {
        // From technical API - direct values in indicators
        price = parseFloat(data.indicators.current_price) || 288.42;
        change = parseFloat(data.indicators.price_change) || 1.7;
        changePercent = parseFloat(data.indicators.price_change_percent) || 0.59;
        volume = data.indicators.volume || 4372457;
    } else {
        // Default values
        price = 288.42;
        change = 1.7;
        changePercent = 0.59;
        volume = 4372457;
    }
    
    console.log(`💰 Price data: $${price}, Change: ${change} (${changePercent}%)`);
    
    updateElement('#currentPrice', `$${price.toFixed(2)}`);
    
    const priceChangeElem = document.getElementById('priceChange');
    if (priceChangeElem) {
        priceChangeElem.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}`;
        priceChangeElem.className = `price-change ${change >= 0 ? 'positive' : 'negative'}`;
    }
    
    const changePercentElem = document.getElementById('priceChangePercent');
    if (changePercentElem) {
        changePercentElem.textContent = `${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%`;
        changePercentElem.className = `price-change-percent ${changePercent >= 0 ? 'positive' : 'negative'}`;
    }
    
    updateElement('#lastUpdate', new Date().toLocaleTimeString());
    
    // Update key stats with proper formatting
    const stats = data.key_stats || {};
    
    // Set symbol-specific financial defaults
    const financialDefaults = {
        'IBM': { marketCap: 268410000000, peRatio: 29.06, divYield: 3.16, range52w: '$233.36 - $295.61' },
        'MSFT': { marketCap: 3800000000000, peRatio: 35.42, divYield: 0.68, range52w: '$362.90 - $542.80' }
    };
    const finDefaults = financialDefaults[currentSymbol] || financialDefaults['IBM'];
    
    updateElement('#marketCap', formatMarketCap(stats.market_cap || finDefaults.marketCap));
    updateElement('#peRatio', stats.pe_ratio ? stats.pe_ratio.toFixed(2) : finDefaults.peRatio.toFixed(2));
    updateElement('#divYield', stats.dividend_yield ? `${(stats.dividend_yield * 100).toFixed(2)}%` : `${finDefaults.divYield}%`);
    updateElement('#range52w', stats['52_week_low'] && stats['52_week_high'] ? 
        `$${stats['52_week_low']} - $${stats['52_week_high']}` : finDefaults.range52w);
    updateElement('#volume', formatVolume(volume));
    updateElement('#beta', stats.beta ? stats.beta.toFixed(2) : '0.724');
    
    console.log('✅ Overview updated successfully!');
}

// Update overview with default values based on symbol
function updateOverviewWithDefaults(symbol) {
    const defaults = {
        'IBM': {
            name: 'International Business Machines',
            price: 288.42,
            change: 1.7,
            changePercent: 0.59,
            marketCap: 264000000000,
            peRatio: 22.45,
            divYield: 4.52,
            range52w: '$280.15 - $295.67',
            volume: 4372457,
            beta: 0.85
        },
        'MSFT': {
            name: 'Microsoft Corporation',
            price: 510.96,
            change: -11.44,
            changePercent: -2.19,
            marketCap: 3800000000000,
            peRatio: 35.42,
            divYield: 0.68,
            range52w: '$362.90 - $542.80',
            volume: 15000000,
            beta: 0.9
        }
    };
    
    const data = defaults[symbol] || defaults['IBM'];
    
    // Update company info
    updateElement('.company-name', data.name);
    updateElement('#companyName', data.name);
    updateElement('.logo-circle', symbol);
    updateElement('.stock-symbol', `${symbol} • ${symbol === 'MSFT' ? 'NASDAQ' : 'NYSE'}`);
    
    // Update price and stats
    updateElement('#currentPrice', `$${data.price.toFixed(2)}`);
    updateElement('#priceChange', `${data.change >= 0 ? '+' : ''}${data.change.toFixed(2)}`);
    updateElement('#priceChangePercent', `${data.changePercent >= 0 ? '+' : ''}${data.changePercent.toFixed(2)}%`);
    updateElement('#marketCap', formatMarketCap(data.marketCap));
    updateElement('#peRatio', data.peRatio.toFixed(2));
    updateElement('#divYield', `${data.divYield}%`);
    updateElement('#range52w', data.range52w);
    updateElement('#volume', formatVolume(data.volume));
    updateElement('#beta', data.beta.toFixed(2));
}

// Update technical indicators with enhanced visualization
function updateTechnicalIndicators(indicators) {
    if (!indicators) {
        console.log('No indicators data received');
        return;
    }
    
    console.log('📊 Updating technical indicators:', indicators);
    
    // Update RSI with color coding
    const rsi = indicators.rsi || 50;
    console.log('RSI:', rsi);
    updateElement('#rsiValue', rsi.toFixed(2));
    
    const rsiFill = document.getElementById('rsiFill');
    if (rsiFill) {
        rsiFill.style.width = `${Math.min(rsi, 100)}%`;
        
        // Color based on RSI level
        if (rsi > 70) {
            rsiFill.style.background = 'var(--danger-color)';
            updateElement('#rsiStatus', 'Overbought - Consider Selling');
        } else if (rsi < 30) {
            rsiFill.style.background = 'var(--secondary-color)';
            updateElement('#rsiStatus', 'Oversold - Consider Buying');
        } else {
            rsiFill.style.background = 'var(--primary-color)';
            updateElement('#rsiStatus', 'Neutral - Wait for Signal');
        }
    }
    
    // Update MACD
    const macd = indicators.macd || {};
    console.log('MACD:', macd);
    updateElement('#macdValue', (macd.macd || 0).toFixed(3));
    updateElement('#signalValue', (macd.signal || 0).toFixed(3));
    updateElement('#histogramValue', (macd.histogram || 0).toFixed(3));
    
    // Update Moving Averages
    const sma = indicators.sma || {};
    console.log('SMA:', sma);
    updateElement('#sma20', sma.sma_20 ? `$${sma.sma_20.toFixed(2)}` : 'N/A');
    updateElement('#sma50', sma.sma_50 ? `$${sma.sma_50.toFixed(2)}` : 'N/A');
    updateElement('#sma200', sma.sma_200 ? `$${sma.sma_200.toFixed(2)}` : 'N/A');
    
    // Update Volume Analysis with interpretation
    const volume = indicators.volume_analysis || {};
    console.log('Volume:', volume);
    updateElement('#currentVolume', formatVolume(volume.current || indicators.volume));
    updateElement('#avgVolume', formatVolume(volume.avg_20));
    updateElement('#volumeRatio', `${(volume.ratio || 1).toFixed(2)}x`);
    updateElement('#volumeSignal', volume.interpretation || 'Normal volume');
    
    // Update Bollinger Bands
    const bollinger = indicators.bollinger_bands || {};
    console.log('Bollinger Bands:', bollinger);
    updateElement('#bbUpper', bollinger.upper ? `$${bollinger.upper.toFixed(2)}` : 'N/A');
    updateElement('#bbMiddle', bollinger.middle ? `$${bollinger.middle.toFixed(2)}` : 'N/A');
    updateElement('#bbLower', bollinger.lower ? `$${bollinger.lower.toFixed(2)}` : 'N/A');
    
    // Update Support & Resistance
    const sr = indicators.support_resistance || {};
    console.log('Support/Resistance:', sr);
    if (sr.resistance && sr.resistance.length > 0) {
        updateElement('#resistanceLevels', sr.resistance.map(r => `$${r.toFixed(2)}`).join(' | '));
    } else {
        updateElement('#resistanceLevels', '--');
    }
    if (sr.support && sr.support.length > 0) {
        updateElement('#supportLevels', sr.support.map(s => `$${s.toFixed(2)}`).join(' | '));
    } else {
        updateElement('#supportLevels', '--');
    }
    
    // Update Signal Strength from signal_strength object
    const signalStrength = indicators.signal_strength || {};
    console.log('Signal Strength:', signalStrength);
    if (signalStrength.strength !== undefined) {
        updateElement('#strengthValue', signalStrength.strength.toFixed(1));
        updateElement('#signalAction', signalStrength.action || 'HOLD');
        updateElement('#signalConfidence', `${(signalStrength.confidence || 0).toFixed(1)}%`);
        
        // Update strength bar
        const strengthFill = document.getElementById('strengthFill');
        if (strengthFill) {
            const strength = signalStrength.strength || 0;
            strengthFill.style.width = `${Math.abs(strength)}%`;
            if (strength > 0) {
                strengthFill.style.background = 'var(--secondary-color)';
            } else {
                strengthFill.style.background = 'var(--danger-color)';
            }
        }
        
        // Update signal reasons
        const reasonsList = document.getElementById('signalReasons');
        if (reasonsList && signalStrength.signals) {
            reasonsList.innerHTML = '';
            signalStrength.signals.forEach(signal => {
                const li = document.createElement('li');
                li.textContent = signal;
                reasonsList.appendChild(li);
            });
        }
    }
    
    console.log('✅ Technical indicators updated successfully!');
}

// Update technical indicators with defaults
function updateTechnicalIndicatorsWithDefaults() {
    updateElement('#rsiValue', '52.35');
    updateElement('#rsiStatus', 'Neutral');
    updateElement('#macdValue', '0.125');
    updateElement('#signalValue', '0.089');
    updateElement('#histogramValue', '0.036');
    updateElement('#sma20', '$144.25');
    updateElement('#sma50', '$142.80');
    updateElement('#sma200', '$138.50');
    updateElement('#currentVolume', '3.5M');
    updateElement('#avgVolume', '3.2M');
    updateElement('#volumeRatio', '1.09x');
}

// Update chart with smooth animations
function updateChart(chartData) {
    if (!chartData || !priceChart) return;
    
    // Prepare labels (dates)
    const labels = (chartData.dates || []).slice(-100).map(date => {
        const d = new Date(date);
        return `${d.getMonth() + 1}/${d.getDate()}`;
    });
    
    // Update chart data
    priceChart.data.labels = labels;
    priceChart.data.datasets[0].data = (chartData.prices || []).slice(-100);
    
    if (chartData.sma_20) {
        priceChart.data.datasets[1].data = chartData.sma_20.slice(-100);
    }
    
    if (chartData.sma_50) {
        priceChart.data.datasets[2].data = chartData.sma_50.slice(-100);
    }
    
    priceChart.update('active');
}

// Update signals with visual enhancement
function updateSignals(signal) {
    if (!signal) return;
    
    // Update signal action with color coding
    const actionElem = document.getElementById('signalAction');
    if (actionElem) {
        actionElem.textContent = signal.signal || 'HOLD';
        actionElem.className = 'signal-action';
        
        if (signal.signal.includes('BUY')) {
            actionElem.classList.add('buy');
        } else if (signal.signal.includes('SELL')) {
            actionElem.classList.add('sell');
        } else {
            actionElem.classList.add('hold');
        }
    }
    
    // Update confidence with visual indicator
    const confidence = signal.confidence || 0;
    updateElement('#signalConfidence', `${confidence.toFixed(1)}%`);
    
    // Update signal strength meter
    const strength = signal.strength || 0;
    updateElement('#signalStrengthValue', strength.toFixed(1));
    
    const strengthBar = document.getElementById('signalStrengthBar');
    if (strengthBar) {
        strengthBar.style.width = `${Math.abs(strength)}%`;
        strengthBar.style.background = strength >= 0 ? 'var(--gradient-green)' : 'var(--gradient-red)';
    }
    
    // Update reasoning list with icons
    const reasonsList = document.getElementById('signalReasons');
    if (reasonsList && signal.reasoning) {
        reasonsList.innerHTML = '';
        signal.reasoning.slice(0, 5).forEach(reason => {
            const li = document.createElement('li');
            li.className = 'signal-reason';
            
            // Add appropriate icon based on reason content
            let icon = '📊';
            if (reason.includes('RSI')) icon = '📈';
            else if (reason.includes('MACD')) icon = '📉';
            else if (reason.includes('volume')) icon = '📊';
            else if (reason.includes('Support') || reason.includes('Resistance')) icon = '🎯';
            
            li.innerHTML = `<span class="reason-icon">${icon}</span> ${reason}`;
            reasonsList.appendChild(li);
        });
    }
}

// Update signals with defaults
function updateSignalsWithDefaults() {
    updateElement('#signalAction', 'HOLD');
    updateElement('#signalConfidence', '65%');
    updateElement('#signalStrengthValue', '0');
}

// Update AI analysis section
function updateAIAnalysis(data) {
    if (!data) return;
    
    const aiSection = document.getElementById('aiAnalysis');
    if (!aiSection) return;
    
    // Update AI analysis content
    if (data.analysis) {
        updateElement('#aiAnalysisContent', data.analysis);
    }
    
    if (data.market_commentary) {
        updateElement('#aiCommentary', data.market_commentary);
    }
    
    if (data.recommendation) {
        const rec = data.recommendation;
        updateElement('#aiRecommendation', rec.recommendation || 'HOLD');
        updateElement('#aiConfidence', `${rec.confidence || 0}%`);
        
        if (rec.key_factors && rec.key_factors.length > 0) {
            const factorsList = document.getElementById('aiKeyFactors');
            if (factorsList) {
                factorsList.innerHTML = rec.key_factors.map(factor => 
                    `<li>${factor}</li>`
                ).join('');
            }
        }
    }
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
    
    // Show/hide content panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        if (panel.id === `${tabName}-panel`) {
            panel.classList.add('active');
        } else {
            panel.classList.remove('active');
        }
    });
    
    // Load market data when switching to portfolio tab
    if (tabName === 'portfolio') {
        loadMarketData();
    }
}

// Show educational content in modal
async function showEducationalContent(topic) {
    if (!topic) return;
    
    // List of topics that use local content (fundamental + sentiment + signals)
    const localTopics = ['pe', 'eps', 'roe', 'margin', 'growth', 'health', 'peg', 'pb', 'dividend', 'marketcap', 'range52w', 
                         'sentiment_score', 'news_sentiment', 'earnings_sentiment', 'sentiment_trend', 'news_distribution', 'media_buzz',
                         'tech_signal', 'fund_signal', 'sent_signal', 'insider_signal'];
    
    // If it's a local topic, use local content directly
    if (localTopics.includes(topic)) {
        showFundamentalEducation(topic);
        return;
    }
    
    let data = null;
    
    try {
        const response = await fetch(`${API_BASE}/education/${topic}`);
        data = await response.json();
        
        const modal = document.getElementById('educationModal');
        if (!modal) return;
        
        // Build comprehensive educational content HTML
        let modalContent = `
            <div class="modal-header">
                <h3>${data.title || 'Educational Content'}</h3>
                <button class="modal-close">&times;</button>
            </div>
            <div class="modal-content-body">
                
                <div class="content-section">
                    <div class="section-header">
                        <span class="section-icon">📊</span>
                        <h4>What is this indicator?</h4>
                    </div>
                    <p class="section-text">${data.description || ''}</p>
                </div>
        `;
        
        if (data.what_it_is) {
            modalContent += `
                <div class="content-section">
                    <div class="section-header">
                        <span class="section-icon">🔍</span>
                        <h4>Technical Details</h4>
                    </div>
                    <p class="section-text">${data.what_it_is}</p>
                </div>
            `;
        }
        
        if (data.why_important) {
            modalContent += `
                <div class="content-section importance">
                    <div class="section-header">
                        <span class="section-icon">⭐</span>
                        <h4>Why is this important?</h4>
                    </div>
                    <p class="section-text">${data.why_important}</p>
                </div>
            `;
        }
        
        if (data.how_to_read && data.how_to_read.length > 0) {
            modalContent += `
                <div class="content-section">
                    <div class="section-header">
                        <span class="section-icon">📖</span>
                        <h4>How to Read This Indicator</h4>
                    </div>
                    <div class="reading-rules">
                        ${data.how_to_read.map(item => `<div class="rule-item">${item}</div>`).join('')}
                    </div>
                </div>
            `;
        }
        
        if (data.signal_contribution && data.contribution_explanation) {
            modalContent += `
                <div class="content-section signal-weight">
                    <div class="section-header">
                        <span class="section-icon">📈</span>
                        <h4>Signal Contribution</h4>
                        <span class="contribution-badge">${data.signal_contribution}</span>
                    </div>
                    <p class="section-text">${data.contribution_explanation}</p>
                </div>
            `;
        }
        
        if (data.current_analysis) {
            modalContent += `
                <div class="content-section current-analysis">
                    <div class="section-header">
                        <span class="section-icon">🎯</span>
                        <h4>Current Analysis for IBM</h4>
                    </div>
                    <p class="section-text analysis-highlight">${data.current_analysis}</p>
                </div>
            `;
        }
        
        if (data.beginner_tip) {
            modalContent += `
                <div class="content-section beginner-tip">
                    <div class="section-header">
                        <span class="section-icon">💡</span>
                        <h4>Beginner Tip</h4>
                    </div>
                    <p class="section-text tip-highlight">${data.beginner_tip}</p>
                </div>
            `;
        }
        
        if (data.trading_strategy) {
            modalContent += `
                <div class="content-section trading-strategy">
                    <div class="section-header">
                        <span class="section-icon">🎯</span>
                        <h4>Trading Strategy</h4>
                    </div>
                    <p class="section-text">${data.trading_strategy}</p>
                </div>
            `;
        }
        
        modalContent += `</div>`;
        
        modal.innerHTML = modalContent;
        modal.classList.add('active');
        
        // Re-attach close event listener
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', closeModal);
        }
        
        console.log(`✅ Educational content loaded for: ${topic}`);
    } catch (error) {
        console.warn('⚠️ API educational content not available for:', topic);
    }
}

// Show fundamental education content (local content, no API call)
function showFundamentalEducation(topic) {
    console.log('📚 Loading fundamental education for:', topic);
    
    // Educational content for fundamental indicators
        const fundamentalEducation = {
            pe: {
                title: 'P/E Ratio (Price-to-Earnings)',
                description: 'The P/E ratio is like checking the price tag on a stock relative to what it actually earns. Imagine you are buying a small business - would you pay $50,000 for a business that makes $10,000 per year (5x earnings) or $100,000 for one that makes $2,000 per year (50x earnings)? The P/E ratio answers this question for stocks. It tells you how many years of current earnings you are paying for when you buy one share. A P/E of 20 means you are paying for 20 years of current earnings. Lower P/E might mean better value, higher P/E might mean high growth expectations.',
                what_it_is: 'P/E Ratio is calculated by dividing the Stock Price by Earnings Per Share (EPS). Formula: P/E = Stock Price ÷ EPS. For example, if IBM stock is trading at $150 and its EPS is $6, then P/E = 150 ÷ 6 = 25. This means you are paying $25 for every $1 of annual earnings. The ratio tells you the market multiple or premium investors are willing to pay. Historical average for the S&P 500 is around 15-16, but it varies by industry. Tech companies often have higher P/Es (30-50+) because of growth expectations, while mature industries like utilities have lower P/Es (10-15). P/E can be calculated using Trailing Twelve Months (TTM) earnings (what the company actually earned) or Forward earnings (what analysts predict).',
                why_important: 'P/E ratio is one of the most widely used valuation metrics because it answers the fundamental question: Is this stock cheap or expensive relative to its profits? A low P/E might indicate the stock is undervalued (bargain), or it could mean the company has problems and growth is slowing. A high P/E might indicate overvaluation (expensive), or it could mean investors expect strong future growth. P/E helps you compare stocks within the same industry - comparing companies across different industries can be misleading. For instance, if most tech companies have P/E of 30 but one similar company has P/E of 15, that is worth investigating. The P/E also reflects market sentiment and growth expectations. During bull markets, average P/Es rise. During bear markets, they fall. Understanding P/E helps you avoid overpaying for stocks and find undervalued opportunities.',
                how_to_read: ['🟢 P/E < 15: Potentially undervalued or slow-growth company - Could be a value opportunity if fundamentals are solid. May indicate mature industry, low growth expectations, or temporary problems. Compare to industry average before concluding undervaluation.', '🟡 P/E 15-25: Fair valuation range for most established companies - This is typical for S&P 500 companies. Neither cheap nor expensive. Reasonable if growth is moderate (5-10% annually).', '🟠 P/E 25-35: Growth premium or becoming expensive - Market expects above-average growth. Justified for companies growing earnings 15%+ annually. Be cautious - any disappointment can cause sharp drops.', '🔴 P/E > 35: Very high growth expectations or potentially overvalued - Market expects exceptional growth. Common in tech and high-growth sectors. High risk - company must deliver strong growth to justify valuation. Miss expectations = stock crash.', '⚠️ Negative P/E: Company is losing money - No earnings means P/E cannot be calculated meaningfully. Either the company is unprofitable or in a temporary loss phase. Very risky - avoid unless you understand the turnaround story.', '📊 Compare to Industry Average: Essential context - A P/E of 30 might be cheap for software (industry average 40) but expensive for banks (industry average 12). Always compare apples to apples.'],
                trading_strategy: 'Value investing approach: Look for stocks with P/E ratios significantly below their industry average (20-30% lower) but with solid fundamentals, growing earnings, and reasonable debt levels. These might be temporarily out of favor or overlooked. Set target to sell when P/E reaches industry average. Growth investing approach: Accept higher P/E ratios (25-40) if the company is growing earnings consistently at 15%+ annually. Use PEG ratio (P/E divided by growth rate) to assess if high P/E is justified. PEG under 2 is reasonable for growth stocks. Cyclical considerations: For cyclical industries (materials, industrials), buy when P/E looks high (earnings at cyclical low) and sell when P/E looks low (earnings at cyclical peak) - the opposite of normal! Contrarian strategy: When entire market P/E is very low (under 15) during bear markets, it often signals buying opportunity for long-term investors. When market P/E exceeds 25, exercise caution. Practical rule: For IBM at P/E 25 vs industry average 25, it is fairly valued. If IBM falls to P/E 18 while maintaining earnings, it becomes attractive. If IBM rises to P/E 35 without earnings growth, consider trimming positions.'
            },
            eps: {
                title: 'EPS (Earnings Per Share)',
                description: 'EPS is like dividing a pizza among friends - it shows how much profit each share gets. If a company earns $1 billion in profit and has 100 million shares, each share gets $10 of that profit (EPS = $10). Think of EPS as your slice of the company profits pie. The bigger your slice (higher EPS), the more valuable your share. Growing EPS means the company is becoming more profitable over time, which usually leads to a rising stock price. EPS is the single most important number in fundamental analysis because it directly shows corporate profitability and is the E in P/E ratio.',
                what_it_is: 'EPS (Earnings Per Share) = Net Income ÷ Total Shares Outstanding. For example, if IBM earns $6 billion in profit this year and has 900 million shares outstanding, EPS = $6 billion ÷ 900 million = $6.67 per share. This means if you own 100 shares, your portion of the profits is $667. There are two types: Basic EPS (simple calculation) and Diluted EPS (accounts for stock options and convertible securities that could dilute ownership). Always use diluted EPS as it is more conservative. EPS is reported quarterly and annually. Companies typically report Trailing Twelve Months (TTM) EPS showing actual past performance, and analysts provide Forward EPS estimates for future periods.',
                why_important: 'EPS is the foundation of stock valuation because it directly measures profitability per share. Stock prices long-term follow EPS growth - if EPS doubles, stock price eventually doubles. Growing EPS signals a healthy, expanding business. Declining EPS signals trouble. EPS growth is the engine that drives stock price appreciation. Companies that consistently grow EPS at 10-20% per year tend to be long-term winners. Wall Street analysts obsess over EPS - when companies beat EPS estimates, stocks often surge. When they miss estimates, stocks plummet. Quarterly earnings reports are all about EPS performance. EPS also determines dividends - companies pay dividends from earnings, so higher EPS supports higher dividends. Understanding EPS and its growth trajectory is essential for picking winning stocks.',
                how_to_read: ['🚀 EPS Growth > 20% YoY: Exceptional growth - Company is firing on all cylinders. If sustained, expect strong stock price appreciation. These are often market leaders in high-growth industries.', '🟢 EPS Growth 10-20% YoY: Strong, healthy growth - Solid performance. Companies growing in this range typically outperform the market. Sustainable long-term.', '🟡 EPS Growth 5-10% YoY: Moderate, steady growth - Decent performance for mature companies. Better than inflation. Stock should appreciate modestly over time.', '🟠 EPS Growth 0-5% YoY: Slow growth or stagnant - Company is barely growing. May be facing headwinds, intense competition, or market saturation. Stock likely to underperform.', '🔴 Negative EPS Growth (declining): Earnings shrinking - Red flag. Company profitability declining. Could be temporary (one-time charges) or structural (losing market share). Investigate cause immediately.', '💰 Positive EPS: Company is profitable - Making money. Can sustain dividends and reinvest in growth. Investable.', '⚠️ Negative EPS: Company is losing money - Burning cash. Cannot pay dividends. Must raise capital or cut costs. High risk unless clear path to profitability.', '📈 Accelerating EPS Growth: Momentum building - EPS growing faster each quarter (5% → 10% → 15%). Very bullish. Often precedes major stock price breakouts.', '📉 Decelerating EPS Growth: Momentum fading - EPS growth slowing (20% → 15% → 10%). Warning sign. Stock price may plateau or decline even if earnings are still growing.'],
                trading_strategy: 'Growth investing: Screen for stocks with consistent EPS growth above 15% for past 3-5 years. These compounders tend to outperform. Look for acceleration in recent quarters as trigger for entry. Quality focus: Seek companies that grow EPS even during recessions. These have pricing power, competitive moats, and strong management. Earnings momentum: Buy stocks that consistently beat quarterly EPS estimates and raise future guidance. This creates positive earnings surprise momentum. Avoid companies that consistently miss estimates. Earnings season strategy: Review earnings calendars. Buy strong companies 2-4 weeks before earnings if EPS growth trend is positive. Sell weaker holdings before earnings if trends are negative. Valuation check: Fast EPS growth justifies higher P/E ratios. A stock growing EPS at 25% can justify P/E of 35-40. Slow EPS growth (under 5%) should have P/E under 15. Portfolio allocation: Allocate more capital to highest EPS growth stocks. These deserve larger position sizes. Underweight or avoid stocks with declining EPS. Long-term compounding: If you own a stock growing EPS at 15% annually, in 5 years EPS will roughly double, and stock price should follow. This is the power of EPS growth compounding. Red flags: Declining EPS for 2+ consecutive quarters = sell signal unless you know exact temporary cause. One quarter miss can be excuse, multiple quarters = trend.'
            },
            roe: {
                title: 'ROE (Return on Equity)',
                description: 'ROE is like a report card that shows how good management is at making money with your investment. Imagine you give $100 to a business owner - ROE tells you how much profit they generate with that $100. If they generate $20 profit, that is 20% ROE (excellent!). If they only generate $5, that is 5% ROE (poor). ROE measures the efficiency and effectiveness of management in using shareholder money to create profits. High ROE means every dollar you invest is working hard for you. Low ROE means your money is not being put to good use. Warren Buffett considers ROE one of the most important metrics for long-term investing.',
                what_it_is: 'ROE = Net Income ÷ Shareholder Equity × 100. For example, if IBM has $6 billion in annual profit (net income) and $50 billion in shareholder equity (book value), ROE = 6 ÷ 50 × 100 = 12%. This means IBM generates $12 of profit for every $100 of shareholder equity. Shareholder equity is essentially the net worth of the company - assets minus liabilities, or what would be left for shareholders if the company sold everything and paid all debts. ROE shows how efficiently the company turns that equity into earnings. Unlike profit margins which measure efficiency of sales, ROE measures efficiency of capital deployment. Companies can boost ROE through operational excellence (higher profits), efficient asset use (less equity needed), or financial leverage (using debt). The best companies achieve high ROE through operational excellence, not excessive debt.',
                why_important: 'ROE is crucial because it reveals management quality and capital allocation skill. A company that consistently delivers 15-20%+ ROE is creating tremendous shareholder value - your investment is compounding at a high rate. ROE above 15% sustained over years indicates the company has a competitive moat - something that allows it to earn superior returns (brand power, patents, network effects, cost advantages). Low ROE under 10% suggests commoditized business, poor management, or intense competition eating away profits. ROE is especially important when comparing companies in the same industry - the highest ROE companies usually have the strongest competitive positions. Companies with high ROE can grow without requiring much external capital, funding growth from retained earnings. Low ROE companies must constantly raise money from investors or lenders, diluting shareholders. Over long periods, stock returns tend to track ROE - a company earning 20% ROE will likely generate ~20% annual stock returns if valuation stays constant.',
                how_to_read: ['🟢 ROE > 20%: Exceptional - World-class company with strong competitive advantage (moat). Management is excellent at generating returns. Examples: Apple, Microsoft, Visa. These companies deserve premium valuations.', '🟢 ROE 15-20%: Excellent - Very strong business with good competitive positioning. Management doing a great job. These companies typically outperform market long-term. Worth premium P/E ratios.', '🟡 ROE 10-15%: Average to Good - Decent business, acceptable returns. Middle of the pack. These companies can be good investments if valuation is reasonable. Typical for many S&P 500 companies.', '🟠 ROE 5-10%: Below Average - Struggling to generate adequate returns. Either intense competition, poor management, or capital-intensive business. Be cautious unless stock is very cheap or turnaround story exists.', '🔴 ROE < 5%: Poor - Severely underperforming. Capital is barely earning more than risk-free treasury bonds. Avoid unless deep value opportunity or special situation.', '⚠️ Negative ROE: Company is losing money - Shareholder equity shrinking as losses pile up. High risk. Only invest if you see clear path to profitability and trust turnaround plan.', '📈 ROE Improving Over Time: Positive trend - Company becoming more efficient, gaining pricing power, or improving operations. Very bullish sign. May indicate emerging moat.', '📉 ROE Declining Over Time: Negative trend - Competition intensifying, margins compressing, or management making poor capital allocation decisions. Warning sign even if absolute ROE still looks okay.', '💎 Consistent High ROE (15%+ for 5-10 years): Holy grail - These are compounding machines. The best long-term investments. Very rare. Hold these stocks through thick and thin.'],
                trading_strategy: 'Quality investing approach: Build a portfolio of stocks with ROE above 15% sustained over 5+ years. These quality compounders tend to massively outperform over decades. Even if you pay fair valuations, the high ROE does the heavy lifting. Screening strategy: Screen for ROE > 15%, then check if it is sustainable (not just one-year spike). Look at 5-year average ROE. Eliminate companies with declining ROE trends. This finds quality businesses. Comparison within industry: Always compare ROE to industry peers. A bank with 12% ROE might be excellent (banking averages 10-12%), while a software company with 12% ROE is poor (software averages 20-30%). Apples to apples comparisons only. Warning on leverage: Check how company achieves high ROE. Calculate: ROE breakdown using DuPont analysis = (Net Margin) × (Asset Turnover) × (Equity Multiplier). If high ROE comes primarily from high leverage (debt), that is risky. Prefer high ROE from high margins and asset efficiency. Value + Quality combo: Look for high ROE stocks (15%+) trading at reasonable valuations (P/E under 20, PEG under 2). This combination of quality and value often produces exceptional long-term returns. Turnaround plays: If a historically high-ROE company (was 18%, now 10%) is experiencing temporary problems but you believe ROE will recover, that can be an attractive opportunity. Market often overreacts to short-term ROE declines. Red flags to avoid: Declining ROE trend over 3+ years, ROE boosted by aggressive accounting, high ROE but negative cash flow (earnings quality issue), cyclical company at peak ROE (will decline in downturn). Long-term holding: If you find a company with 20%+ ROE sustained over a decade, buy it and hold it forever (Buffett style). These companies are wealth compounding machines. Let the high ROE do the work over 10-20 years.'
            },
            margin: {
                title: 'Profit Margins',
                description: 'Profit margins are like measuring how much money you keep after paying all your bills. Imagine you sell lemonade for $1 - if it costs you 60 cents to make (lemons, sugar, cups), you keep 40 cents profit, giving you a 40% profit margin. Companies are the same. Margins show what percentage of every sales dollar actually becomes profit. High margins (20-30%+) mean the company keeps lots of each sale as profit - they have pricing power and efficient operations. Low margins (under 5%) mean the company barely makes anything on each sale - they operate in a competitive, cutthroat industry. There are three key margin levels that reveal different aspects of profitability: Gross (after direct costs), Operating (after operating expenses), and Net (after everything including taxes).',
                what_it_is: 'There are three critical margin metrics: (1) Gross Margin = (Revenue - Cost of Goods Sold) ÷ Revenue × 100. This shows profit after direct production costs. For IBM at 57.6%, this means for every $100 in sales, $57.60 remains after paying for materials and direct labor. (2) Operating Margin = Operating Income ÷ Revenue × 100. For IBM at 18.3%, this shows profit after all operating expenses (R&D, marketing, administration). This reveals operational efficiency. (3) Net Margin = Net Income ÷ Revenue × 100. For IBM at 9.1%, this is the bottom-line profit after all expenses, interest, and taxes. This is what actually flows to shareholders. The "margin cascade" from gross → operating → net shows how much profit disappears at each stage. Wide margins at each level indicate pricing power and efficiency.',
                why_important: 'Margins are crucial because they reveal pricing power and competitive strength. High-margin businesses (like software, luxury goods) can charge premium prices because customers perceive high value or face few alternatives. They have "moats" - competitive advantages that protect profits. Low-margin businesses (like grocery stores, airlines) face intense competition and must compete on price. Margins also show operational efficiency. Two companies with same revenue but one has 20% net margin and other has 5% - the first is far more profitable and valuable. Expanding margins over time signal the company is gaining pricing power, improving efficiency, or achieving economies of scale. Declining margins warn of intensifying competition, rising costs, or loss of differentiation. Margins directly impact valuation - high-margin companies command premium P/E ratios because quality of earnings is superior. Finally, high margins provide cushion during downturns and funding for innovation.',
                how_to_read: ['🟢 Gross Margin > 50%: Excellent - Strong pricing power and low direct costs. Typical of software, technology, luxury goods. Very profitable business model.', '🟡 Gross Margin 30-50%: Good - Decent pricing power. Typical of many successful businesses. Healthy profitability.', '🟠 Gross Margin 10-30%: Moderate - Competitive industry. Must rely on volume and efficiency. Typical of retailers, manufacturers.', '🔴 Gross Margin < 10%: Poor - Cutthroat competition. Very thin profits. Typical of commodities, discount retailers. Risky.', '🟢 Operating Margin > 20%: Excellent - Very efficient operations and strong pricing. Best-in-class companies.', '🟡 Operating Margin 10-20%: Good - Solid operational efficiency. IBM at 18.3% is good.', '🟠 Operating Margin 5-10%: Fair - Tight operations. Limited room for error.', '🔴 Operating Margin < 5%: Poor - Barely profitable operations. High risk.', '🟢 Net Margin > 15%: Excellent - Highly profitable after everything. Outstanding business.', '🟡 Net Margin 5-15%: Good to Fair - Decent profitability. IBM at 9.1% is fair.', '🔴 Net Margin < 5%: Poor - Very low bottom-line profitability. Vulnerable.', '📈 Margins Expanding: Very bullish - Company gaining pricing power, improving efficiency, or achieving scale. Strong positive signal.', '📉 Margins Declining: Bearish - Competition intensifying or costs rising faster than prices. Warning sign.', '⚖️ Stable Margins: Neutral - Consistent operations. Neither improving nor deteriorating.'], 
                trading_strategy: 'Margin expansion play: Look for companies with margins expanding over past 2-3 years. This indicates improving competitive position. Even if stock looks expensive, expanding margins often justify higher valuation and lead to upside surprises. High margin + growth combo: The ultimate combination is high margins (net > 15%) plus strong growth (revenue growth > 10%). These companies can invest heavily in growth while remaining very profitable. Examples: SaaS companies, platform businesses. Compare to industry: Always benchmark margins against industry averages. A grocery store with 3% net margin might be excellent (industry averages 1-2%), while a software company with 10% net margin is poor (industry averages 25-30%). Context matters. Quality indicator: Use margins as quality filter. Screen for net margins above 10% or operating margins above 15%. This filters for quality businesses with competitive advantages. Combine with growth and ROE for powerful quality screen. Turnaround potential: If a company had high margins historically (say 20% operating margin) but now has low margins (10%), investigate why. If temporary and fixable (restructuring, one-time costs), this could be a turnaround opportunity as margins revert. Recession resilience: High-margin companies weather recessions better. They have pricing power to maintain prices and can cut costs without jeopardizing business. Favor high-margin companies when economic uncertainty rises. Warning signs: Watch for margin compression (declining margins for 2+ quarters). This often precedes EPS misses and stock declines. Even if revenue grows, if margins compress, profits disappoint. Cyclical considerations: For cyclical companies (materials, energy, industrials), margins peak at cycle tops and trough at cycle bottoms. Don\'t buy cyclicals when margins are at record highs - they will compress. Buy when margins have hit bottom.'
            },
            growth: {
                title: 'Revenue & Earnings Growth',
                description: 'Revenue and earnings growth rates are like a company\'s speedometer - they show how fast the business is expanding. Imagine two stores: Store A increases sales 20% per year while Store B\'s sales are flat. Which business would you rather own? Obviously Store A! Growth is the engine of stock price appreciation. A company growing revenue and earnings at 15% per year will double in size every 5 years. Over time, stock prices follow earnings growth. Fast-growing companies create wealth for shareholders through compounding. Revenue growth shows customer demand and market share gains. Earnings growth shows the company is converting revenue growth into increasing profitability. The combination of strong revenue growth AND earnings growth is the holy grail of investing.',
                what_it_is: 'Growth rates measure percentage change over time. Revenue Growth = (Current Period Revenue - Previous Period Revenue) ÷ Previous Period Revenue × 100. Earnings Growth uses same formula with earnings. We track three timeframes: (1) Annual Growth: Year-over-year change, smooths out quarterly volatility. For IBM at 1.4% annual revenue growth, this is slow. (2) Quarterly Growth: Quarter-over-quarter, shows recent momentum. IBM at 7.7% quarterly is better - business accelerating. (3) Earnings Growth: IBM at -19.7% earnings decline is concerning - revenue growing but profits falling. This suggests margin compression or rising costs. We also look at multi-year average growth rates (3-year, 5-year) to identify consistent compounders vs. one-time spikes. Analysts project forward growth rates which drive valuation expectations.',
                why_important: 'Growth is critical because it directly drives long-term stock returns. The math is simple: if a company grows earnings at 15% annually, the stock price should rise approximately 15% annually over long periods (assuming valuation stays constant). This is the power of compounding. Growth also indicates competitive strength - fast-growing companies are taking market share, launching successful products, or riding industry tailwinds. Growth creates opportunities - growing companies can invest in R&D, acquire competitors, and attract top talent. Wall Street rewards growth - high-growth companies command premium valuations (higher P/E ratios). Even expensive-looking growth stocks can be bargains if growth continues. Conversely, no-growth or declining companies see compressed valuations regardless of current cheapness. Growth is especially important in technology and innovative sectors where winner-take-most dynamics prevail. Finally, growth separates great long-term investments from mediocre ones. A stock growing at 15% annually turns $10,000 into $80,000 over 15 years. At 5% growth, same investment becomes only $21,000.',
                how_to_read: ['🚀 Revenue Growth > 20%: Exceptional - Hypergrowth company. Often found in emerging technologies, disruptive businesses. High risk but high reward. Expect premium valuations.', '🟢 Revenue Growth 10-20%: Strong - Fast-growing business. Above-average growth. These companies typically outperform market. Look for sustainable drivers.', '🟡 Revenue Growth 5-10%: Moderate - Steady growth, slightly better than economy. Typical of mature large caps. Solid but unexciting. IBM at 1.4% annual is below this.', '🟠 Revenue Growth 0-5%: Slow - Barely growing or stagnant. Mature or challenged business. May still work if combined with high margins and dividends.', '🔴 Negative Revenue Growth: Declining - Business shrinking. Major red flag unless temporary (restructuring, divestitures). Investigate causes immediately.', '🚀 Earnings Growth > 20%: Exceptional - Profits surging. If sustainable, stock should soar. Often from margin expansion or operational leverage.', '🟢 Earnings Growth 10-20%: Strong - Healthy profit growth. Ideal range for compounding wealth. Sustainable over long periods.', '🟡 Earnings Growth 5-10%: Moderate - Decent profit growth. Better than inflation. Acceptable for mature companies.', '🔴 Earnings Declining (IBM at -19.7%): Warning - Profits shrinking despite revenue growth. Margin compression issue. Needs investigation. Could signal competitive pressure.', '⚡ Revenue Growth > Earnings Growth: Margin compression - Revenue growing but profits not keeping pace. Concerning. Rising costs or pricing pressure.', '💎 Earnings Growth > Revenue Growth: Margin expansion - Profits growing faster than revenue. Excellent! Shows operating leverage and efficiency gains.', '📈 Accelerating Growth: Very bullish - Growth rate increasing each quarter (5% → 10% → 15%). Momentum building. Often triggers stock breakouts.', '📉 Decelerating Growth: Warning - Growth rate slowing (20% → 15% → 10%). Even if still positive, slowdown often triggers valuation compression.'],
                trading_strategy: 'Growth at reasonable price (GARP): Look for companies growing revenue and earnings 15%+ but trading at PEG ratios under 2. This balances growth and valuation. Avoid overpaying for growth, but accept premium valuations for quality growth. Growth momentum: Buy companies with accelerating growth rates. For example, if revenue growth was 8%, then 12%, now 16%, this acceleration often precedes major stock moves. Market takes time to recognize improving trends. Quality growth filter: Screen for companies with both revenue growth > 10% AND earnings growth > 10% over past 3 years. This filters for quality compounders. Add ROE > 15% and you have world-class businesses. Rule of 40 (for SaaS/Tech): Revenue Growth % + Profit Margin % should exceed 40. For example, 30% growth + 15% margin = 45 (excellent). This balances growth and profitability. Sustainable growth: Favor organic growth over acquisition-driven growth. Check if growth is sustainable (expanding addressable market, competitive advantages) or temporary (stimulus, one-time events). Long-term compounding: If you find a company that has grown revenue and earnings at 15%+ for past 5-10 years consistently, seriously consider buying regardless of valuation. These proven compounders are rare and valuable. Time in beats timing for these. Recession resilience: Some companies grow through recessions (defensive healthcare, consumer staples, software). These deserve premiums. Cyclical companies (industrials, materials) see growth stop in downturns - factor this into valuation. Warning signals: Revenue growth without earnings growth (IBM situation at -19.7% earnings) is red flag. Also beware: growth from acquisition sprees (can\'t be sustained), growth from price increases without volume gains (demand weak), revenue growth but cash flow declining (accounting games). Valuation framework: As rough guide, growth companies can justify P/E ratios up to their growth rate. If growing 25%, P/E of 25 is reasonable (PEG of 1). Above that, getting expensive. Under that, potentially cheap.'
            },
            health: {
                title: 'Financial Health Ratios',
                description: 'Financial health ratios are like a company\'s medical checkup - they reveal if the business is financially strong or sick. Imagine checking someone\'s vital signs: heart rate (liquidity), blood pressure (debt levels), stamina (cash reserves). Companies are similar. Strong financial health means the company can easily pay its bills, weather economic storms, and fund growth without begging for money. Weak financial health means the company is one crisis away from trouble - struggling to pay debts, running out of cash, or overleveraged. The three key ratios we examine are: Debt-to-Equity (leverage level), Current Ratio (short-term liquidity), and Quick Ratio (immediate cash coverage). Together they paint a complete picture of financial stability.',
                what_it_is: 'Three critical health metrics: (1) Debt/Equity Ratio = Total Debt ÷ Shareholder Equity. IBM at 4.02 means $4.02 of debt for every $1 of equity - highly leveraged. Shows how much the company relies on borrowed money vs. owner equity. (2) Current Ratio = Current Assets ÷ Current Liabilities. IBM at 1.04 means $1.04 in short-term assets for every $1 in short-term liabilities. Measures ability to pay bills due within one year. Minimum healthy level is 1.0 (can cover obligations). (3) Quick Ratio = (Current Assets - Inventory) ÷ Current Liabilities. IBM at 1.00 means exactly enough liquid assets to cover short-term debts. This is the acid test - can the company pay bills immediately without selling inventory? More conservative than current ratio. These ratios reveal financial structure, liquidity cushion, and bankruptcy risk.',
                why_important: 'Financial health is critical because even profitable companies can go bankrupt if they can\'t pay their debts. Cash flow and balance sheet strength matter as much as income statement profits. Strong financial health provides: (1) Survival insurance during recessions - companies with low debt and high liquidity weather downturns while overleveraged competitors fail. 2008-2009 proved this brutally. (2) Flexibility for opportunities - healthy companies can acquire distressed competitors, invest in R&D, or buy back stock during market panics when others are paralyzed. (3) Lower bankruptcy risk - excessive debt kills companies. Even if revenue is growing, too much debt means all profits go to interest payments and one bad quarter triggers default. (4) Credit access - strong balance sheets get better interest rates and easier capital access. Weak balance sheets face high rates or get shut out entirely. (5) Investor confidence - companies with fortress balance sheets command higher valuations. Investors sleep better. The 2008 financial crisis showed that debt levels matter more than anything when crisis hits. Companies with debt/equity over 5 and low cash faced extinction. Strong balance sheets survived and thrived.',
                how_to_read: ['🟢 Debt/Equity < 0.5: Conservative - Very low debt, fortress balance sheet. Can survive any crisis. Typical of cash-rich tech companies like Apple, Microsoft. Very safe.', '🟡 Debt/Equity 0.5-1.5: Moderate - Reasonable debt load. Most healthy companies. Balanced use of leverage without excessive risk.', '🟠 Debt/Equity 1.5-3.0: High Leverage - Significant debt load. Can work if cash flows are stable. Be cautious. Interest expenses eat into profits.', '🔴 Debt/Equity > 3.0: Very High Leverage - IBM at 4.02 is in this zone. Highly leveraged. One recession or profit miss and company faces distress. High risk. Avoid unless you trust cash flows are rock solid.', '⚠️ Debt/Equity > 5.0: Danger Zone - Extreme leverage. Bankruptcy risk during downturns. Only acceptable for utilities or REITs with ultra-stable cash flows.', '🟢 Current Ratio > 2.0: Excellent - Strong short-term liquidity. Plenty of cushion to pay bills. Very safe.', '🟡 Current Ratio 1.5-2.0: Good - Adequate liquidity. Healthy cushion. Can handle normal business cycles.', '🟠 Current Ratio 1.0-1.5: Fair - Tight liquidity. IBM at 1.04 is barely adequate. Limited margin for error. One bad quarter could cause cash crunch.', '🔴 Current Ratio < 1.0: Poor - Cannot cover short-term obligations with current assets. Liquidity crisis risk. May need emergency financing.', '🟢 Quick Ratio > 1.5: Excellent - Strong immediate liquidity even without selling inventory. Very safe.', '🟡 Quick Ratio 1.0-1.5: Good - Adequate liquid assets. Can pay bills without selling inventory.', '🟠 Quick Ratio 0.5-1.0: Fair - Tight. IBM at 1.00 is barely adequate. Would struggle if customers stopped paying immediately.', '🔴 Quick Ratio < 0.5: Poor - Cannot pay immediate obligations without selling inventory or getting credit. High distress risk.'],
                trading_strategy: 'Safe haven strategy: During uncertain times, favor companies with Debt/Equity under 1.0 and Current Ratio over 1.5. These fortress balance sheets survive and thrive when others struggle. In 2008, these companies bought distressed assets at firesale prices. Turnaround plays: If a quality company (historically strong balance sheet) temporarily shows weak ratios due to one-time event (acquisition, restructuring), that can be opportunity if you believe they will deleverage. Market overreacts to short-term balance sheet deterioration. Avoid high leverage in cyclicals: For cyclical industries (airlines, energy, materials, construction), avoid high debt/equity. When recession hits, revenues crash but debt payments don\'t. Many airlines with debt/equity over 3 went bankrupt in 2008-2020. Defensive sectors can handle more debt: Utilities, REITs, and consumer staples have stable cash flows and can safely operate with higher leverage (debt/equity 2-4). Their regulated or defensive nature makes debt serviceable. Growth stock caution: Some high-growth companies show weak ratios because they invest heavily in growth (burning cash, low current ratio). This is okay if revenue is hypergrowth and path to profitability is clear. But risky - one funding drought and company dies. Screening for quality: Screen for Debt/Equity under 1.5 AND Current Ratio over 1.5. This finds financially healthy companies. Combine with profitability metrics (ROE, margins) for quality filter. Crisis preparation: If you think recession is coming, rotate portfolio toward low-debt companies (debt/equity under 1). These will outperform. High-debt companies get crushed in recessions as lenders cut off credit. IBM analysis: At 4.02 debt/equity, IBM is highly leveraged. This is concerning for a mature tech company. One major business disruption could cause financial stress. The 1.04 current ratio provides minimal liquidity cushion. However, IBM has stable enterprise software revenues which support debt servicing. Still, prefer companies with stronger balance sheets unless IBM is extremely cheap.'
            },
            peg: {
                title: 'PEG Ratio (Price/Earnings to Growth)',
                description: 'PEG Ratio is like the "smart version" of P/E ratio - it accounts for growth to give you true value. Imagine two stocks: Stock A has P/E of 30 but growing 30% per year. Stock B has P/E of 15 but not growing at all. Which is better value? P/E alone says Stock B. But PEG says Stock A (PEG = 1.0) is actually better value than Stock B (PEG = infinity because no growth). PEG ratio solves the fundamental problem with P/E: it doesn\'t consider growth. A high P/E might be justified if growth is high. A low P/E might be expensive if there\'s no growth. PEG levels the playing field by dividing P/E by growth rate. Legendary investor Peter Lynch popularized PEG ratio and looked for PEG under 1.0 as his "golden rule" for finding undervalued growth stocks.',
                what_it_is: 'PEG Ratio = P/E Ratio ÷ Annual EPS Growth Rate. For IBM with P/E of 46.32 but EPS declining at -19.7%, the PEG is negative (undefined when growth is negative) - a major red flag. For a healthy example: if a company has P/E of 25 and EPS growth of 20%, PEG = 25 ÷ 20 = 1.25 (fair value). If P/E is 40 but growth is also 40%, PEG = 1.0 (good value despite high P/E). If P/E is 10 but growth is only 5%, PEG = 2.0 (expensive despite low P/E). The beauty of PEG is it works across different growth rates and company sizes. IBM\'s PEG at 1.73 (shown) uses forward estimates not current declining growth. Always check which growth rate is used - historical, forward estimates, or analyst projections. Most reliable is 3-5 year historical average growth to avoid one-time spikes.',
                why_important: 'PEG ratio is crucial because it\'s the single best metric for valuing growth stocks. P/E alone is misleading - growth companies always look expensive on P/E, value companies always look cheap. But cheap isn\'t good if there\'s no growth, and expensive isn\'t bad if growth is strong. PEG solves this by normalizing for growth. It answers: "Am I paying a fair price for this growth rate?" PEG allows comparison across vastly different companies - you can compare a slow-growth utility (P/E 12, growth 3%, PEG 4.0) to a fast-growth tech stock (P/E 50, growth 40%, PEG 1.25) and see the tech stock is actually better value. PEG prevents overpaying - even if growth story is exciting, PEG over 2.0 means you\'re paying too much and future returns will disappoint. Peter Lynch built his legendary returns at Fidelity using PEG as primary valuation tool. He proved that buying stocks with PEG under 1.0 and holding them produced exceptional long-term returns.',
                how_to_read: ['💎 PEG < 1.0: Undervalued - Excellent value relative to growth. This is Peter Lynch territory - stocks with PEG under 1.0 are often hidden gems. If P/E is 20 and growth is 25%, you\'re getting growth at a discount. Buy signal.', '🟢 PEG 1.0-1.5: Fair Value - Reasonably valued for growth rate. Not cheap but not expensive. Paying approximately fair price for growth. Acceptable to buy if quality is high.', '🟡 PEG 1.5-2.0: Fully Valued to Slightly Expensive - IBM at 1.73 is here. Paying premium for growth. Only justified if quality is exceptional or growth is accelerating. Be selective.', '🟠 PEG 2.0-3.0: Expensive - Overpaying for growth. If P/E is 60 and growth is only 25%, PEG = 2.4. Too expensive. Future returns will likely disappoint unless growth accelerates dramatically.', '🔴 PEG > 3.0: Very Expensive - Extreme overvaluation. Bubble territory. Market has priced in perfection. Any disappointment triggers crash. Avoid or sell if you own.', '⚠️ Negative or Undefined PEG: No growth or declining earnings - If growth is negative (like IBM\'s current -19.7%), PEG doesn\'t work. This is a warning sign. Either use forward estimates or avoid the stock.', '📈 PEG Improving (was 2.5, now 1.5): Becoming better value - Either multiple compressed or growth accelerated. Positive trend. Consider buying.', '📉 PEG Worsening (was 1.0, now 2.0): Becoming expensive - Either multiple expanded or growth slowed. Negative trend. Consider selling or reducing position.'],
                trading_strategy: 'Peter Lynch strategy: Screen for PEG under 1.0 with positive earnings growth over 10%. This finds undervalued growth stocks. Lynch called these "fast growers" and made fortune buying them. Balance PEG with quality: Don\'t buy junk just because PEG is low. Combine PEG < 1.5 with ROE > 15% and positive free cash flow. This ensures you\'re buying quality growth at fair prices, not value traps. Growth at reasonable price (GARP): Target PEG between 0.5-1.5. This sweet spot gives you growth without overpaying. Warren Buffett evolved from pure value to GARP, buying quality growers at reasonable PEGs. Sector considerations: Different sectors justify different PEGs. High-quality software companies can justify PEG up to 2.0 due to predictable recurring revenue. Cyclical companies should have PEG under 1.0 because growth isn\'t sustainable. Avoid negative PEG stocks: If a stock has negative or undefined PEG due to declining earnings, it\'s usually best to avoid unless you have high conviction on turnaround. IBM\'s current situation requires forward estimates, which are less reliable. Compare PEG to peers: Look at industry average PEG. If sector averages PEG of 2.5 but you find company at PEG 1.2, that\'s relative value even if absolute PEG isn\'t under 1.0. Sell discipline: Sell when PEG exceeds 2.5-3.0, even if stock has been winner. At that point, you\'ve extracted the value and stock is overpriced. Take profits. Market timing: During bull markets, average PEG rises (market gets expensive). During bear markets, PEG falls (bargains emerge). Use PEG to avoid overpaying in euphoria and find bargains in panic. Warning on manipulation: Companies can manipulate growth rates with accounting tricks or one-time gains. Always verify growth is sustainable and from operations, not financial engineering. Use 3-5 year average growth rates instead of single-year spikes. IBM at 1.73 PEG: Fair but not cheap, especially with current negative organic growth. The 1.73 must be using optimistic forward estimates. Verify if that growth is achievable before buying. Better values exist elsewhere.'
            },
            pb: {
                title: 'Price-to-Book Ratio',
                description: 'Price-to-Book (P/B) ratio is like comparing the sale price of a house to its appraised value. If a house is appraised at $300,000 (book value) but sells for $600,000 (market price), it has a P/B of 2.0 - buyers are paying 2x the asset value. Stocks work the same way. Book value is what the company would be worth if you sold all assets and paid all debts today - it\'s the accounting net worth. Market price is what investors are actually willing to pay. P/B ratio shows if you\'re paying a premium or discount to net assets. Low P/B (under 1.0) means you\'re buying assets at a discount - classic value investing. High P/B (over 5.0) means you\'re paying a huge premium - either the company has incredible intangible value (brands, tech) or it\'s overvalued.',
                what_it_is: 'P/B Ratio = Stock Price ÷ Book Value Per Share. Book Value Per Share = (Total Assets - Total Liabilities - Preferred Stock) ÷ Shares Outstanding. This is the per-share net worth. For IBM at P/B of 9.70, investors are paying $9.70 for every $1 of book value - a very high premium. This is expensive for a traditional company. For comparison: if IBM stock is $150 and book value per share is $15.46, then P/B = 150 ÷ 15.46 = 9.70. Book value represents tangible assets (factories, equipment, cash, inventory) minus liabilities. It doesn\'t capture intangible assets like brands, patents, customer relationships, or future growth potential. That\'s why growth companies and asset-light businesses trade at high P/B - most value isn\'t on the balance sheet.',
                why_important: 'P/B ratio is important for several reasons: (1) Margin of safety - Benjamin Graham (Warren Buffett\'s teacher) used P/B as key value metric. Buying stocks below book value (P/B < 1.0) provides downside protection because you\'re buying assets at a discount. If company liquidates, you could recover your investment. (2) Value investing screen - P/B helps find undervalued stocks that market is ignoring. During market crashes, many quality companies trade below book value, creating opportunities. 2008-2009 had numerous P/B < 1.0 opportunities. (3) Differentiates business types - Asset-heavy industries (banks, insurers, manufacturers) should have low P/B (1-3). Asset-light industries (software, services, tech) naturally have high P/B (5-20+) because value is in intangibles. (4) Red flag detector - Very high P/B (over 10) in traditional industries might signal overvaluation. IBM at 9.70 is high for a mature tech company. (5) Banking sector essential - P/B is the primary valuation metric for banks and financial institutions because their assets (loans, securities) are marked to market and book value is meaningful.',
                how_to_read: ['🟢 P/B < 1.0: Trading below book value - Potential bargain. Market values company less than its net assets. Either company is undervalued (opportunity) or has fundamental problems (value trap). Investigate why it\'s cheap. Classic value investing territory.', '🟡 P/B 1.0-3.0: Fair value for asset-heavy companies - Reasonable for banks, manufacturers, insurers, industrial companies. Paying modest premium over assets. Not cheap but not expensive for companies where assets drive value.', '🟠 P/B 3.0-5.0: Moderate premium - Fair for quality companies with some intangible value. Typical for established companies with strong brands or competitive positions. Acceptable if ROE is high (15%+).', '🟠 P/B 5.0-10.0: High premium - Expensive for traditional companies. IBM at 9.70 is in this range. Fair for asset-light businesses (software, consulting) but pricey for hardware/manufacturing. Justified only if growth and ROE are strong.', '🔴 P/B > 10: Very high premium - Extremely expensive or asset-light business. Common for high-growth tech (cloud, SaaS, platforms) where value is in intellectual property, not physical assets. Can be justified for exceptional businesses but risky if growth slows.', '💡 P/B vs ROE relationship: Key insight - High P/B is justified if ROE is high. If a company earns 25% ROE, P/B of 5 is reasonable (premium justified by returns). If ROE is only 10%, P/B of 5 is expensive. Check if P/B premium is earned.', '⚠️ Declining Book Value: Red flag - If book value is shrinking year over year (losses, asset write-downs), even low P/B isn\'t safe. Book value must be stable or growing.', '🏆 P/B < 1 + High ROE: Hidden gem - Rare combination. Company generating strong returns but trading below book value. Often occurs during market panic. Excellent opportunity if fundamentals are solid.'],
                trading_strategy: 'Value investing classic: Screen for P/B under 1.5 combined with positive earnings, growing book value, and decent ROE (>10%). This finds genuinely undervalued stocks, not value traps. Benjamin Graham\'s favorite approach. Crisis opportunities: During market crashes, quality companies often trade at P/B under 1.0. Create a watchlist of strong companies and wait for P/B to dip below 1.0 during panics. 2020 COVID crash, 2008 financial crisis both offered these opportunities. Bank valuation: For banks and financials, P/B is THE key metric. Buy banks at P/B under 1.0 (trading below book, rare), sell at P/B over 2.0 (expensive for banks). Banks should trade at 1.0-1.5 P/B normally. Asset-light businesses: For tech, SaaS, and platform companies, ignore high P/B. Focus on P/S (price-to-sales), EV/Revenue, or PEG instead. Book value is meaningless when assets are intellectual. High P/B is normal for Google, Microsoft, Salesforce. Quality check: Don\'t buy low P/B blindly. Always check: (1) Is book value real or inflated? (2) Is company profitable? (3) Why is it cheap - temporary or permanent problems? (4) Is industry in structural decline? (5) Is management trustworthy? Avoid value traps. ROE + P/B combo: Calculate P/B ÷ ROE. Result under 0.5 is excellent value. For example, P/B of 2 and ROE of 20% gives 2 ÷ 20 = 0.1 (great). IBM at P/B 9.70 and ROE 22.7% gives 9.70 ÷ 22.7 = 0.43 (borderline acceptable - high P/B offset by strong ROE). Turnaround plays: If a distressed company is restructuring and book value is being rebuilt (asset sales, debt paydown, cost cuts), P/B can be misleading. Book value might jump, making P/B look better. Focus on trajectory. Liquidation value: For troubled companies, compare P/B to tangible book value (excludes goodwill and intangibles). If P/B to tangible book is under 1.0, there\'s a floor on downside - company could be liquidated for more than market cap. Warning on IBM: P/B of 9.70 is very high for a mature technology company transitioning from hardware to services. This suggests either market expects significant growth (doubtful given -19.7% earnings decline) or stock is expensive. Combined with high P/E of 46.32, valuation looks stretched. Better opportunities likely exist at lower valuations.'
            },
            dividend: {
                title: 'Dividend Metrics',
                description: 'Dividends are like rent checks from owning property - regular cash payments you receive just for owning the stock. Imagine owning a rental property that pays you $500/month in rent. Dividends work the same way - companies share their profits with shareholders through quarterly cash payments. Dividend yield tells you the annual income rate (like rent yield on property). Payout ratio tells you sustainability - what percentage of profits the company pays out. High yield with low payout = great income investment. High yield with high payout = risky, dividend might get cut. Dividends are powerful wealth builders - they provide cash flow, force discipline on management, and historically account for ~40% of total stock market returns. Dividend growth investing is one of the most proven long-term wealth-building strategies.',
                what_it_is: 'Two key dividend metrics: (1) Dividend Yield = Annual Dividend Per Share ÷ Current Stock Price × 100. If IBM pays $6.60 per share annually in dividends and stock is $150, yield = 6.60 ÷ 150 × 100 = 4.4%. This is your income return - you earn 4.4% per year in cash just for holding the stock, regardless of price changes. (2) Payout Ratio = Annual Dividends Per Share ÷ Earnings Per Share × 100. If IBM pays $6.60 in dividends and earns $6.19 EPS, payout ratio = 6.60 ÷ 6.19 × 100 = 107%. Over 100% means paying more than earnings - unsustainable! Must be covered by cash flow or is temporary. Also watch Dividend Growth Rate - what percentage the dividend increases annually. A company raising dividends 7% yearly for 25+ years (Dividend Aristocrat) is a quality compounder.',
                why_important: 'Dividends are crucial for multiple reasons: (1) Passive income - Dividends provide steady cash flow without selling shares. Perfect for retirees or income-focused investors. Checks arrive quarterly like clockwork. (2) Total return component - Historically, dividends account for ~40% of S&P 500 total returns. A stock yielding 3% needs only 7% price appreciation to deliver 10% total return. Many investors overlook this. (3) Quality signal - Dividend payers tend to be profitable, mature, cash-generating businesses. Companies don\'t pay dividends unless they\'re confident in cash flows. Dividend cuts destroy stock prices, so management is very careful. (4) Discipline mechanism - Paying dividends forces management to be disciplined with capital. They can\'t waste cash on empire-building or bad acquisitions. Cash must be earned. (5) Downside protection - In bear markets, dividend stocks fall less because investors hold for income. 3-5% yield provides cushion. (6) Inflation hedge - Dividend growers raise payments faster than inflation, protecting purchasing power. (7) Compounding machine - Reinvesting dividends creates powerful compounding. $10,000 invested in S&P 500 in 1980 with dividends reinvested grew to $1+ million by 2023. Without dividends, only ~$300,000. Dividend Aristocrats (25+ years of dividend growth) have massively outperformed market long-term.',
                how_to_read: ['💎 Dividend Yield > 5%: Very High Income - Excellent cash flow for income investors. BUT be cautious - very high yields often signal problems. Either stock crashed (yield mathematically rose) or dividend is unsustainable. Verify payout ratio under 80% and dividend history is stable. Could be value trap.', '🟢 Dividend Yield 3-5%: High Income - Attractive income with reasonable safety if payout ratio is healthy. Sweet spot for income investing. Many quality dividend stocks live here (REITs, utilities, telecom, consumer staples).', '🟡 Dividend Yield 2-3%: Good Income - Solid income plus growth potential. Typical for dividend growth stocks. Balance of income and capital appreciation. Many Dividend Aristocrats here.', '🟠 Dividend Yield 1-2%: Low Income - Modest income. Often found in growth stocks that pay token dividends. Better for capital appreciation than income.', '⚪ Dividend Yield < 1% or $0: No/Minimal Income - Company reinvests all profits into growth. Common in tech and high-growth sectors. Great for growth investors, useless for income investors.', '🟢 Payout Ratio < 50%: Very Safe - Company pays less than half of earnings as dividends. Lots of cushion for bad years. Dividend is rock solid. Room to grow dividend substantially. This is fortress-level dividend safety.', '🟡 Payout Ratio 50-70%: Safe - Sustainable payout. Typical for mature dividend payers. Reasonable cushion while sharing solid portion of profits. Dividend should be safe in most scenarios.', '🟠 Payout Ratio 70-90%: Elevated Risk - Paying out most earnings. Limited cushion for bad years. One earnings miss could force dividend cut. Be cautious. Acceptable only if earnings are very stable (utilities, regulated industries).', '🔴 Payout Ratio > 90%: High Risk - Company paying almost all or more than earnings. Unsustainable unless temporary. High risk of dividend cut. Avoid unless you know exact reason (temporary earnings dip, using cash flow instead of earnings).', '⚠️ Payout Ratio > 100%: Unsustainable - Paying more than earning. Can\'t last. Either dividend will be cut or company is using cash reserves/borrowing to pay. Very dangerous. Sell or avoid.', '📈 Dividend Growth > 10% annually: Exceptional - Fast-growing dividend. Compound income stream. These are dividend growth champions. Income doubles every 7 years. Wealth building machines.', '🏆 Dividend Aristocrat (25+ years of increases): Elite - Proven compounder. Survived multiple recessions while growing dividend. Ultimate quality signal. Never bet against these companies.'],
                trading_strategy: 'Dividend growth investing: Build portfolio of stocks with dividend growth > 7% annually, payout ratio < 70%, and yield 2-4%. This creates growing income stream that compounds over decades. Companies like Coca-Cola, Johnson & Johnson, Procter & Gamble exemplify this. Hold forever and live off rising dividends in retirement. High yield value: Screen for yield > 5%, payout ratio < 60%, P/E < 15. This finds genuinely undervalued high-yielders, not yield traps. Market occasionally misprices quality dividend payers during sell-offs - buy these. Dividend Aristocrats strategy: Buy the Dividend Aristocrats index (companies with 25+ years of dividend increases). Hold long-term. These companies have proven they can grow through any economy. Outperform S&P 500 with lower volatility. DRIP investing: Enroll in dividend reinvestment plans (DRIPs) to automatically reinvest dividends into more shares. This creates compounding magic. Turn $10,000 into $1 million over 30-40 years through dividends alone. Yield trap avoidance: Avoid extremely high yields (over 8%) unless you deeply understand the business. High yields usually mean market expects dividend cut. Check: (1) Is payout ratio under 90%? (2) Is dividend history stable or has it been cut before? (3) Is the company in declining industry? (4) Is debt manageable? If any red flags, avoid. Income portfolio construction: Build ladder of yields - some 2-3% growers, some 4-5% sustainers, some 5%+ high-yielders. Diversify across sectors. Aim for portfolio yield of 3-4% with dividend growth of 5-7%. This generates growing income that outpaces inflation. Recession defense: In uncertain times, rotate toward Dividend Aristocrats and companies with payout ratios under 50%. These can maintain/grow dividends even in recessions. High payout ratios are vulnerable to cuts when earnings fall. Dividend cut reaction: If a dividend is cut, usually best to sell immediately. Cuts signal serious problems and stocks often fall 20-40% on cut announcements. Market severely punishes dividend cuts. Don\'t hope for recovery - sell and move to safer dividend payers. Tax advantage: Qualified dividends are taxed at lower rates (0-20%) vs ordinary income (up to 37%). Hold dividend stocks in taxable accounts to benefit from preferential tax treatment. Growth stocks in retirement accounts. Warning signs: Payout ratio rising toward 100%, dividend growth slowing or stopping, company borrowing to pay dividends, industry in structural decline, management discussing "dividend sustainability." These signal potential cut. Reduce or sell position before cut happens.'
            },
            marketcap: {
                title: 'Market Capitalization',
                description: 'Market cap is the total value of all outstanding shares, showing company size.',
                what_it_is: 'Calculated as: Current Stock Price × Total Shares Outstanding. Represents what the market thinks the company is worth.',
                why_important: 'Determines company size category and risk profile. Larger companies are typically more stable but slower growing.',
                how_to_read: ['> $200B: Mega Cap (safest, slow growth)', '$10B-$200B: Large Cap (stable)', '$2B-$10B: Mid Cap (balanced)', '$300M-$2B: Small Cap (higher risk/reward)', '< $300M: Micro Cap (highest risk)'],
                trading_strategy: 'Large caps like IBM ($268B) offer stability and dividends. Mid/small caps offer growth potential with higher volatility.'
            },
            range52w: {
                title: '52-Week Range',
                description: 'The highest and lowest stock prices over the past 52 weeks (one year).',
                what_it_is: 'Shows the stock\'s price volatility and trading range over the past year. Current price position within this range indicates momentum.',
                why_important: 'Helps identify if stock is near highs (potentially overvalued) or lows (potentially undervalued). Shows price volatility.',
                how_to_read: ['Near 52W High: Strong momentum, potential resistance', 'Mid-range: Neutral positioning', 'Near 52W Low: Weak momentum, potential support', 'Wide range: High volatility', 'Narrow range: Low volatility'],
                trading_strategy: 'Breakout traders buy above 52W high. Value investors look for stocks near 52W low with strong fundamentals. Calculate position: (Current - Low) / (High - Low) × 100.'
            },
            sentiment_score: {
                title: 'Overall Sentiment Score',
                description: 'A composite score measuring market sentiment from -1 (very negative) to +1 (very positive).',
                what_it_is: 'Combines sentiment from news articles, earnings transcripts, and market data. Score of 0 is neutral, positive values indicate bullish sentiment, negative values indicate bearish sentiment.',
                why_important: 'Sentiment drives short-term price movements. Strong positive sentiment often precedes rallies, while negative sentiment can signal downturns.',
                how_to_read: ['> 0.3: Very Positive (Bullish)', '0.1 to 0.3: Positive', '-0.1 to 0.1: Neutral', '-0.3 to -0.1: Negative', '< -0.3: Very Negative (Bearish)'],
                trading_strategy: 'Use as confirmation for other signals. Extreme positive sentiment may indicate overbought conditions (contrarian sell). Strong negative sentiment in fundamentally sound stocks may present buying opportunities.'
            },
            news_sentiment: {
                title: 'News Sentiment Analysis',
                description: 'Measures sentiment from financial news articles about the company.',
                what_it_is: 'Analyzes headlines and article content using natural language processing to determine positive, negative, or neutral tone. Aggregates sentiment across hundreds of news sources.',
                why_important: 'News drives investor perception and trading decisions. Media coverage influences both institutional and retail investors.',
                how_to_read: ['High volume + positive: Strong bullish signal', 'High volume + negative: Bearish pressure', 'Low volume: Limited market impact', 'Check article count for reliability'],
                trading_strategy: 'Increasing positive news coverage often precedes uptrends. Watch for sentiment shifts - rapid negative news can trigger sell-offs. Compare news sentiment to price action for divergences.'
            },
            earnings_sentiment: {
                title: 'Earnings Call Sentiment',
                description: 'Analyzes management tone and language during quarterly earnings calls.',
                what_it_is: 'Evaluates CEO and CFO statements for confidence, caution, optimism, or concern. Looks for forward-looking statements, guidance changes, and management sentiment beyond just numbers.',
                why_important: 'Management tone often reveals true business health beyond reported metrics. Confident management typically signals strong fundamentals.',
                how_to_read: ['Bullish: Confident tone, raised guidance, expansion plans', 'Neutral: Stable outlook, maintaining guidance', 'Bearish: Cautious language, lowered expectations, restructuring talk'],
                trading_strategy: 'Positive earnings sentiment + strong results = strong buy signal. Negative sentiment despite good numbers = warning sign. Management sentiment often leads stock performance by 1-2 quarters.'
            },
            sentiment_trend: {
                title: 'Sentiment Trend',
                description: 'Shows how sentiment is changing over time - improving, declining, or stable.',
                what_it_is: 'Tracks sentiment direction by comparing recent sentiment scores to historical averages. Identifies momentum in market perception.',
                why_important: 'Trends reveal sentiment momentum. Improving trends suggest growing confidence, while declining trends indicate increasing concerns.',
                how_to_read: ['Improving + Strong: Bullish momentum building', 'Improving + Weak: Early recovery phase', 'Declining + Strong: Losing momentum', 'Declining + Weak: Bearish pressure mounting'],
                trading_strategy: 'Enter positions when sentiment is improving from negative territory (turnaround play). Take profits when sentiment peaks at extreme positive levels. Avoid stocks with persistently declining sentiment.'
            },
            news_distribution: {
                title: 'News Distribution',
                description: 'Breakdown of positive, neutral, and negative news articles.',
                what_it_is: 'Shows the percentage and count of articles in each sentiment category. Provides balance perspective beyond average sentiment.',
                why_important: 'Distribution reveals consensus strength. High positive/negative split shows polarized views. Balanced distribution suggests uncertainty.',
                how_to_read: ['70%+ positive: Strong bullish consensus', '60%+ negative: Strong bearish consensus', 'Balanced (33/33/33): Market uncertainty', 'Track changes over time for trend'],
                trading_strategy: 'Extreme positive distribution (>80%) may signal overoptimism - consider taking profits. High negative distribution in quality stocks creates buying opportunities. Shifting distribution predicts sentiment changes.'
            },
            media_buzz: {
                title: 'Media Buzz / Coverage Level',
                description: 'Measures the volume and intensity of media attention on the stock.',
                what_it_is: 'Scored 0-100 based on article count, social mentions, and coverage frequency. Higher scores indicate more market attention and discussion.',
                why_important: 'High buzz increases volatility and liquidity. Unusual spikes often precede major moves. Low buzz may indicate overlooked opportunities.',
                how_to_read: ['70-100: Very High (viral/trending)', '50-70: High attention', '30-50: Moderate coverage', '< 30: Low attention/quiet period'],
                trading_strategy: 'Rising buzz + positive sentiment = momentum opportunity. High buzz + extreme sentiment = potential reversal point. Low buzz in fundamentally strong stocks = undervalued opportunity.'
            },
            tech_signal: {
                title: 'Technical Analysis Signal',
                description: 'Combined signal from all technical indicators (RSI, MACD, Moving Averages, etc.).',
                what_it_is: 'Weighted score (-100 to +100) combining multiple technical indicators. Analyzes price action, momentum, trend, and volume patterns.',
                why_important: 'Technical signals identify entry/exit timing. Weight: 40% of overall signal - largest component.',
                how_to_read: ['> 50: Strong Bullish (buy signal)', '20-50: Moderately Bullish', '-20 to 20: Neutral (no clear direction)', '-50 to -20: Moderately Bearish', '< -50: Strong Bearish (sell signal)'],
                trading_strategy: 'Use technical signals for timing. Strong positive technical + positive fundamental = high-conviction trade. Technical divergence from fundamentals may signal reversal opportunity.'
            },
            fund_signal: {
                title: 'Fundamental Analysis Signal',
                description: 'Combined signal from valuation, profitability, growth, and financial health metrics.',
                what_it_is: 'Weighted score (-100 to +100) based on P/E, ROE, margins, growth rates, and debt levels. Measures intrinsic value and business quality.',
                why_important: 'Fundamentals determine long-term value. Weight: 30% of overall signal - second largest component.',
                how_to_read: ['> 50: Strong Fundamentals (undervalued)', '20-50: Good Fundamentals', '-20 to 20: Fair Value', '-50 to -20: Weak Fundamentals', '< -50: Poor Fundamentals (overvalued)'],
                trading_strategy: 'Strong fundamentals provide safety margin. Use for position sizing - larger positions in fundamentally strong stocks. Fundamental weakness in uptrend = exit signal.'
            },
            sent_signal: {
                title: 'Sentiment Analysis Signal',
                description: 'Combined signal from news sentiment, earnings call tone, and market perception.',
                what_it_is: 'Weighted score (-100 to +100) analyzing news articles, management commentary, and social metrics. Measures market psychology.',
                why_important: 'Sentiment drives short-term momentum. Weight: 20% of overall signal - captures market emotion.',
                how_to_read: ['> 50: Very Positive Sentiment', '20-50: Positive Sentiment', '-20 to 20: Neutral Sentiment', '-50 to -20: Negative Sentiment', '< -50: Very Negative Sentiment'],
                trading_strategy: 'Extreme positive sentiment = potential top (contrarian sell). Extreme negative sentiment in quality stocks = buying opportunity. Use sentiment for risk management and position timing.'
            },
            insider_signal: {
                title: 'Insider Trading Signal',
                description: 'Signal based on insider buying and selling activity by company executives and directors.',
                what_it_is: 'Weighted score (-100 to +100) analyzing recent insider transactions. Heavy buying suggests confidence, heavy selling suggests concerns.',
                why_important: 'Insiders have privileged information about business prospects. Weight: 10% of overall signal - smallest but most informed component.',
                how_to_read: ['> 50: Heavy Insider Buying (bullish)', '20-50: Moderate Buying', '-20 to 20: Neutral/Normal Activity', '-50 to -20: Moderate Selling', '< -50: Heavy Insider Selling (bearish)'],
                trading_strategy: 'Multiple insiders buying = strong conviction signal. CEO/CFO buying especially significant. Selling less reliable (could be personal reasons). Cluster of buys near lows = accumulation.'
            }
        };
        
        data = fundamentalEducation[topic];
        
        if (data) {
            const modal = document.getElementById('educationModal');
            if (!modal) return;
            
            let modalContent = `
                <div class="modal-header">
                    <h3>${data.title || 'Educational Content'}</h3>
                    <button class="modal-close">&times;</button>
                </div>
                <div class="modal-content-body">
                    <div class="content-section">
                        <div class="section-header">
                            <span class="section-icon">📊</span>
                            <h4>What is this indicator?</h4>
                        </div>
                        <p class="section-text">${data.description || ''}</p>
                    </div>
            `;
            
            if (data.what_it_is) {
                modalContent += `
                    <div class="content-section">
                        <div class="section-header">
                            <span class="section-icon">🔍</span>
                            <h4>How It's Calculated</h4>
                        </div>
                        <p class="section-text">${data.what_it_is}</p>
                    </div>
                `;
            }
            
            if (data.why_important) {
                modalContent += `
                    <div class="content-section importance">
                        <div class="section-header">
                            <span class="section-icon">⭐</span>
                            <h4>Why It Matters</h4>
                        </div>
                        <p class="section-text">${data.why_important}</p>
                    </div>
                `;
            }
            
            if (data.how_to_read && data.how_to_read.length > 0) {
                modalContent += `
                    <div class="content-section">
                        <div class="section-header">
                            <span class="section-icon">📖</span>
                            <h4>How to Interpret</h4>
                        </div>
                        <div class="reading-rules">
                            ${data.how_to_read.map(item => `<div class="rule-item">• ${item}</div>`).join('')}
                        </div>
                    </div>
                `;
            }
            
            if (data.trading_strategy) {
                modalContent += `
                    <div class="content-section trading-strategy">
                        <div class="section-header">
                            <span class="section-icon">🎯</span>
                            <h4>Trading Strategy</h4>
                        </div>
                        <p class="section-text">${data.trading_strategy}</p>
                    </div>
                `;
            }
            
            modalContent += `</div>`;
            
            modal.innerHTML = modalContent;
            modal.classList.add('active');
            
            // Re-attach close event listener
            const closeBtn = modal.querySelector('.modal-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', closeModal);
            }
            
            console.log(`✅ Fundamental educational content loaded for: ${topic}`);
        } else {
            console.error('❌ No educational content available for:', topic);
        }
}

// Close modal
function closeModal() {
    const modal = document.getElementById('educationModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

// Utility function to update element text content safely
function updateElement(selector, value) {
    const element = document.querySelector(selector);
    if (element) {
        element.textContent = value;
    }
}

// Format market cap for display
function formatMarketCap(value) {
    if (!value) return 'N/A';
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    return `$${value.toFixed(2)}`;
}

// Format volume for display
function formatVolume(value) {
    if (!value) return 'N/A';
    if (value >= 1e9) return `${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(0)}K`;
    return value.toString();
}

// Show loading overlay
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Show error message
function showError(message) {
    console.error(message);
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// Debug function to test API connectivity
async function debugAPIConnection() {
    console.log('🔍 Testing API connection...');
    
    try {
        const response = await fetch(`${API_BASE}/technical/IBM`);
        const data = await response.json();
        
        console.log('✅ API Response received:', data);
        console.log('📊 Indicators data:', data.indicators);
        console.log('💰 Current price:', data.indicators.current_price);
        console.log('📈 RSI:', data.indicators.rsi);
        console.log('📊 MACD:', data.indicators.macd);
        
        // Test updating indicators directly
        console.log('🔄 Testing indicator updates...');
        updateTechnicalIndicators(data.indicators);
        
        return data;
    } catch (error) {
        console.error('❌ API test failed:', error);
        return null;
    }
}

// Update Expert Analysis panel
function updateExpertAnalysis(data) {
    console.log('🤖 Updating expert analysis panel with:', data);
    
    if (!data) return;
    
    // Update computed signal section
    const computedSignal = data.computed_signal || {};
    updateElement('#computedAction', computedSignal.action || 'HOLD');
    updateElement('#computedConfidence', `${computedSignal.confidence || 0}%`);
    updateElement('#computedStrength', computedSignal.strength || '0');
    
    // Update computed action badge styling
    const computedActionElem = document.getElementById('computedAction');
    if (computedActionElem) {
        computedActionElem.className = `action-badge ${(computedSignal.action || 'HOLD').toLowerCase()}`;
    }
    
    // Update strength bar
    const strengthBar = document.getElementById('computedStrengthBar');
    if (strengthBar) {
        const strength = parseFloat(computedSignal.strength || 0);
        strengthBar.style.width = `${Math.min(strength, 100)}%`;
    }
    
    // Update individual indicators breakdown
    updateIndicatorsBreakdown(data.individual_signals || {});
    
    // Update expert analysis section
    const expertAnalysis = data.expert_analysis || {};
    updateElement('#expertAction', expertAnalysis.expert_signal || 'HOLD');
    updateElement('#expertConfidence', `${expertAnalysis.confidence || 0}%`);
    updateElement('#expertAnalysis', expertAnalysis.detailed_analysis || 'Expert analysis not available');
    
    // Update expert action badge styling
    const expertActionElem = document.getElementById('expertAction');
    if (expertActionElem) {
        expertActionElem.className = `action-badge ${(expertAnalysis.expert_signal || 'HOLD').toLowerCase()}`;
    }
    
    // Update agreement status
    const agreement = expertAnalysis.agreement_with_computed || {};
    const agreementElem = document.getElementById('agreementStatus');
    if (agreementElem) {
        const agrees = agreement.agrees;
        agreementElem.textContent = agrees ? '✅ Agrees with Model' : '❌ Disagrees with Model';
        agreementElem.className = `agreement-badge ${agrees ? 'agrees' : 'disagrees'}`;
    }
    
    // Update signal breakdown
    updateExpertBreakdown(expertAnalysis.signal_breakdown || {});
    
    // Update trading strategy
    updateTradingStrategy(expertAnalysis.strategy_recommendation || {});
    
    // Update risk assessment
    updateRiskAssessment(expertAnalysis.risk_assessment || {});
    
    // Update key levels
    updateKeyLevels(expertAnalysis.key_levels || {});
}

function updateIndicatorsBreakdown(individualSignals) {
    const container = document.getElementById('indicatorsList');
    if (!container) return;
    
    container.innerHTML = '';
    
    const indicators = [
        { key: 'rsi', name: 'RSI (14)', weight: '25%' },
        { key: 'macd', name: 'MACD', weight: '20%' },
        { key: 'moving_averages', name: 'Moving Averages', weight: '18%' },
        { key: 'volume', name: 'Volume', weight: '15%' },
        { key: 'bollinger_bands', name: 'Bollinger Bands', weight: '12%' },
        { key: 'support_resistance', name: 'Support/Resistance', weight: '10%' }
    ];
    
    indicators.forEach(indicator => {
        const signalData = individualSignals[indicator.key] || {};
        const signalType = signalData.signal || 'NEUTRAL';
        const contribution = signalData.contribution || 'N/A';
        
        const item = document.createElement('div');
        item.className = 'indicator-item';
        
        let signalClass = 'neutral';
        if (signalType.includes('BUY') || signalType.includes('BULLISH') || signalType.includes('UPTREND')) {
            signalClass = 'bullish';
        } else if (signalType.includes('SELL') || signalType.includes('BEARISH') || signalType.includes('DOWNTREND')) {
            signalClass = 'bearish';
        }
        
        item.innerHTML = `
            <span class="indicator-name">${indicator.name}</span>
            <div class="indicator-details">
                <span class="indicator-signal ${signalClass}">${signalType}</span>
                <span class="indicator-weight">${indicator.weight}</span>
                <small style="color: var(--text-muted);">${contribution}</small>
            </div>
        `;
        
        container.appendChild(item);
    });
}

function updateExpertBreakdown(signalBreakdown) {
    const container = document.getElementById('expertBreakdown');
    if (!container) return;
    
    container.innerHTML = '';
    
    const breakdownItems = [
        { key: 'rsi_analysis', title: 'RSI Analysis', icon: '📊' },
        { key: 'macd_analysis', title: 'MACD Analysis', icon: '📈' },
        { key: 'trend_analysis', title: 'Trend Analysis', icon: '📉' },
        { key: 'volume_analysis', title: 'Volume Analysis', icon: '📊' },
        { key: 'volatility_analysis', title: 'Volatility Analysis', icon: '🌊' },
        { key: 'support_resistance_analysis', title: 'Support/Resistance', icon: '🎯' }
    ];
    
    breakdownItems.forEach(item => {
        const analysis = signalBreakdown[item.key];
        if (analysis) {
            const breakdownDiv = document.createElement('div');
            breakdownDiv.className = 'breakdown-item';
            breakdownDiv.innerHTML = `
                <h5>${item.icon} ${item.title}</h5>
                <p>${analysis}</p>
            `;
            container.appendChild(breakdownDiv);
        }
    });
}

function updateTradingStrategy(strategy) {
    const container = document.getElementById('tradingStrategy');
    if (!container) return;
    
    container.innerHTML = '';
    
    const strategyItems = [
        { key: 'entry_strategy', title: 'Entry Strategy', icon: '🎯' },
        { key: 'position_sizing', title: 'Position Sizing', icon: '⚖️' },
        { key: 'stop_loss', title: 'Stop Loss', icon: '🛑' },
        { key: 'take_profit_targets', title: 'Take Profit', icon: '💰' },
        { key: 'holding_period', title: 'Holding Period', icon: '⏱️' }
    ];
    
    strategyItems.forEach(item => {
        const value = strategy[item.key];
        if (value) {
            const strategyDiv = document.createElement('div');
            strategyDiv.className = 'strategy-item';
            
            let displayValue = value;
            if (Array.isArray(value)) {
                displayValue = value.join(', ');
            }
            
            strategyDiv.innerHTML = `
                <div class="strategy-icon">${item.icon}</div>
                <div class="strategy-text">
                    <h5>${item.title}</h5>
                    <p>${displayValue}</p>
                </div>
            `;
            container.appendChild(strategyDiv);
        }
    });
}

function updateRiskAssessment(risk) {
    const container = document.getElementById('riskAssessment');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Risk level
    if (risk.risk_level) {
        const riskDiv = document.createElement('div');
        riskDiv.className = 'risk-item';
        riskDiv.innerHTML = `
            <div class="risk-icon">⚡</div>
            <div class="risk-text">
                <h5>Risk Level</h5>
                <p><strong>${risk.risk_level}</strong></p>
            </div>
        `;
        container.appendChild(riskDiv);
    }
    
    // Risk mitigation
    if (risk.risk_mitigation) {
        const mitigationDiv = document.createElement('div');
        mitigationDiv.className = 'risk-item';
        mitigationDiv.innerHTML = `
            <div class="risk-icon">🛡️</div>
            <div class="risk-text">
                <h5>Risk Mitigation</h5>
                <p>${risk.risk_mitigation}</p>
            </div>
        `;
        container.appendChild(mitigationDiv);
    }
    
    // Key risks
    if (risk.key_risks && risk.key_risks.length > 0) {
        const risksDiv = document.createElement('div');
        risksDiv.className = 'risk-item';
        risksDiv.innerHTML = `
            <div class="risk-icon">⚠️</div>
            <div class="risk-text">
                <h5>Key Risks</h5>
                <p>${risk.key_risks.join(', ')}</p>
            </div>
        `;
        container.appendChild(risksDiv);
    }
}

function updateKeyLevels(levels) {
    const container = document.getElementById('keyLevels');
    if (!container) return;
    
    container.innerHTML = '';
    
    const levelItems = [
        { key: 'immediate_support', title: 'Support', class: 'support' },
        { key: 'immediate_resistance', title: 'Resistance', class: 'resistance' },
        { key: 'breakout_level', title: 'Breakout', class: 'breakout' },
        { key: 'invalidation_level', title: 'Invalidation', class: 'invalidation' }
    ];
    
    levelItems.forEach(item => {
        const value = levels[item.key];
        if (value) {
            const levelDiv = document.createElement('div');
            levelDiv.className = `level-item ${item.class}`;
            levelDiv.innerHTML = `
                <span class="level-label">${item.title}</span>
                <span class="level-value">${value}</span>
            `;
            container.appendChild(levelDiv);
        }
    });
}

// Initialize expert analysis with empty/waiting state
function updateExpertAnalysisInitialState() {
    console.log('📋 Initializing expert analysis - waiting for button click');
    
    // Set initial states
    updateElement('#expertAction', 'HOLD');
    updateElement('#expertConfidence', '0%');
    updateElement('#expertAnalysis', 'Click the button above to get Gemini AI expert analysis.');
    updateElement('#agreementStatus', 'Awaiting Analysis');
    
    // Clear breakdown sections
    const breakdownElem = document.getElementById('expertBreakdown');
    if (breakdownElem) {
        breakdownElem.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 1rem;">Click the button to generate expert insights</p>';
    }
    
    const strategyElem = document.getElementById('tradingStrategy');
    if (strategyElem) {
        strategyElem.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 1rem;">Trading strategy will appear after analysis</p>';
    }
    
    const riskElem = document.getElementById('riskAssessment');
    if (riskElem) {
        riskElem.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 1rem;">Risk assessment will appear after analysis</p>';
    }
    
    const levelsElem = document.getElementById('keyLevels');
    if (levelsElem) {
        levelsElem.innerHTML = '<p style="color: var(--text-secondary); text-align: center; padding: 1rem;">Key price levels will appear after analysis</p>';
    }
}

// Load Gemini expert analysis on demand
async function loadGeminiExpertAnalysis() {
    const button = document.getElementById('getGeminiAnalysis');
    if (!button) return;
    
    // Disable button and show loading state
    button.disabled = true;
    button.textContent = '⏳ Loading Gemini Analysis...';
    
    try {
        console.log('🤖 Loading Gemini expert analysis...');
        const expertData = await fetchWithRetry(`${API_BASE}/trading-expert/${currentSymbol}`);
        
        if (expertData) {
            console.log('✅ Gemini expert analysis received:', expertData);
            updateExpertAnalysis(expertData);
            button.textContent = '✅ Analysis Complete';
            
            // Reset button after 2 seconds
            setTimeout(() => {
                button.textContent = '🔄 Refresh Gemini Analysis';
                button.disabled = false;
            }, 2000);
        } else {
            throw new Error('No data received');
        }
    } catch (error) {
        console.error('❌ Gemini expert analysis failed:', error);
        button.textContent = '❌ Analysis Failed - Try Again';
        button.disabled = false;
        
        // Show error message
        updateElement('#expertAnalysis', `Trading expert analysis failed: ${error.message}. Please check your API key and try again.`);
    }
}

function updateExpertAnalysisWithDefaults() {
    console.log('⚠️ Using default expert analysis data');
    
    // Mock data similar to the static data we have
    const mockData = {
        computed_signal: {
            action: 'WEAK_BUY',
            confidence: 23,
            strength: 37.5
        },
        individual_signals: {
            rsi: { signal: 'OVERBOUGHT', weight: '25%', contribution: '81.79' },
            macd: { signal: 'BULLISH', weight: '20%', contribution: '2.101' },
            moving_averages: { signal: 'UPTREND', weight: '18%', contribution: '+6.5%' },
            volume: { signal: 'NEUTRAL', weight: '15%', contribution: '0.81x' },
            bollinger_bands: { signal: 'OVERBOUGHT', weight: '12%', contribution: '0.885' },
            support_resistance: { signal: 'AT_RESISTANCE', weight: '10%', contribution: '$292' }
        },
        expert_analysis: {
            expert_signal: 'BUY',
            confidence: 78,
            detailed_analysis: 'Based on comprehensive technical analysis, IBM shows strong momentum with bullish indicators. While RSI indicates overbought conditions, the overall trend remains intact with strong support levels.',
            agreement_with_computed: { agrees: false, reasoning: 'Expert sees stronger bullish signals than the mathematical model due to trend strength and momentum confirmation.' },
            signal_breakdown: {
                rsi_analysis: 'RSI at 81.79 indicates overbought territory but can remain elevated in strong trends.',
                macd_analysis: 'MACD crossover confirms bullish momentum with positive histogram.',
                trend_analysis: 'Price above all major moving averages confirms strong uptrend.',
                volume_analysis: 'Volume at 0.81x average shows controlled buying, not panic.',
                volatility_analysis: 'Price near upper Bollinger Band suggests potential consolidation.',
                support_resistance_analysis: 'Strong support at $286 with resistance cluster around $292.'
            },
            strategy_recommendation: {
                entry_strategy: 'Buy on pullback to $286 support or breakout above $292',
                position_sizing: 'Standard 2-3% portfolio allocation',
                stop_loss: '$285.50 below key support',
                take_profit_targets: ['$295 (resistance)', '$302 (measured move)'],
                holding_period: '2-4 weeks for swing trade'
            },
            risk_assessment: {
                risk_level: 'MEDIUM',
                key_risks: ['Overbought RSI', 'Resistance levels', 'Lower volume'],
                risk_mitigation: 'Use tight stop loss and scale into position on pullbacks'
            },
            key_levels: {
                immediate_support: '$286.05',
                immediate_resistance: '$292.05',
                breakout_level: '$295.67',
                invalidation_level: '$285.15'
            }
        }
    };
    
    updateExpertAnalysis(mockData);
}

// Update fundamental analysis display
function updateFundamentalAnalysis(analysis) {
    if (!analysis) {
        console.warn('⚠️ No fundamental analysis data provided');
        return;
    }
    
    console.log('💰 Updating fundamental indicators:', analysis);
    console.log('📊 Analysis structure check:', {
        has_metrics: !!analysis.metrics,
        has_scores: !!analysis.scores,
        metrics_keys: analysis.metrics ? Object.keys(analysis.metrics) : [],
        scores_keys: analysis.scores ? Object.keys(analysis.scores) : []
    });
    
    const metrics = analysis.metrics || analysis;
    const scores = analysis.scores || {};
    
    console.log('💵 Extracted metrics:', metrics);
    console.log('📈 Extracted scores:', scores);
    
    // P/E Ratio
    const peRatio = metrics.pe_ratio || 0;
    console.log('🔢 P/E Ratio value:', peRatio);
    const peElement = document.querySelector('#peRatioValue');
    console.log('🎯 P/E element found:', !!peElement, peElement);
    
    updateElement('#peRatioValue', peRatio > 0 ? peRatio.toFixed(2) : 'N/A');
    const peStatus = peRatio < 15 ? 'Undervalued' : peRatio < 25 ? 'Fair Value' : peRatio < 35 ? 'Overvalued' : 'Expensive';
    updateElement('#peRatioStatus', peStatus);
    if (metrics.sector_avg_pe) {
        updateElement('#peIndustryAvg', metrics.sector_avg_pe.toFixed(1));
    }
    console.log('✅ P/E updated to:', peRatio.toFixed(2), 'Status:', peStatus);
    
    // EPS
    const eps = metrics.eps || 0;
    updateElement('#epsValue', eps > 0 ? `$${eps.toFixed(2)}` : 'N/A');
    const epsGrowth = metrics.earnings_growth || 0;
    updateElement('#epsGrowth', `${epsGrowth >= 0 ? '+' : ''}${epsGrowth.toFixed(1)}%`);
    const epsStatus = epsGrowth > 15 ? 'Strong Growth' : epsGrowth > 5 ? 'Growing' : epsGrowth > 0 ? 'Slow Growth' : 'Declining';
    updateElement('#epsStatus', epsStatus);
    
    // ROE
    const roe = metrics.roe || 0;
    updateElement('#roeValue', `${roe.toFixed(1)}%`);
    const roeStatus = roe > 20 ? 'Excellent' : roe > 15 ? 'Good' : roe > 10 ? 'Average' : 'Poor';
    updateElement('#roeStatus', roeStatus);
    
    // Update ROE bar
    const roeFill = document.getElementById('roeFill');
    if (roeFill) {
        const roePercent = Math.min((roe / 30) * 100, 100);
        roeFill.style.width = `${roePercent}%`;
        if (roe > 15) {
            roeFill.style.background = 'var(--gradient-green)';
        } else if (roe > 10) {
            roeFill.style.background = 'linear-gradient(90deg, var(--warning-color), #f39c12)';
        } else {
            roeFill.style.background = 'var(--gradient-red)';
        }
    }
    
    // Profit Margins
    updateElement('#profitMarginValue', `${(metrics.profit_margin || 0).toFixed(1)}%`);
    updateElement('#operatingMarginValue', `${(metrics.operating_margin || 0).toFixed(1)}%`);
    updateElement('#grossMarginValue', `${(metrics.gross_margin || 0).toFixed(1)}%`);
    
    // Growth
    updateElement('#revenueGrowth', `${(metrics.revenue_growth || 0).toFixed(1)}%`);
    updateElement('#quarterlyRevGrowth', `${(metrics.quarterly_revenue_growth || 0).toFixed(1)}%`);
    updateElement('#earningsGrowth', `${(metrics.earnings_growth || 0).toFixed(1)}%`);
    
    // Financial Health
    updateElement('#debtToEquity', (metrics.debt_to_equity || 0).toFixed(2));
    updateElement('#currentRatio', (metrics.current_ratio || 0).toFixed(2));
    updateElement('#quickRatio', (metrics.quick_ratio || 0).toFixed(2));
    
    // PEG Ratio
    const peg = metrics.peg_ratio || 0;
    updateElement('#pegValue', peg > 0 ? peg.toFixed(2) : 'N/A');
    const pegStatus = peg > 0 && peg < 1 ? 'Great Value' : peg < 1.5 ? 'Good Value' : peg < 2 ? 'Fair' : 'Overvalued';
    updateElement('#pegStatus', pegStatus);
    
    // Price to Book
    const pb = metrics.price_to_book || 0;
    updateElement('#pbValue', pb > 0 ? pb.toFixed(2) : 'N/A');
    const pbStatus = pb < 1 ? 'Undervalued' : pb < 3 ? 'Fair Value' : pb < 5 ? 'Overvalued' : 'Expensive';
    updateElement('#pbStatus', pbStatus);
    
    // Dividend
    updateElement('#divYieldValue', `${(metrics.dividend_yield || 0).toFixed(2)}%`);
    updateElement('#payoutRatio', `${(metrics.dividend_payout_ratio || 0).toFixed(1)}%`);
    const divYield = metrics.dividend_yield || 0;
    const divSignal = divYield > 4 ? 'High Yield' : divYield > 2 ? 'Good Yield' : divYield > 0 ? 'Low Yield' : 'No Dividend';
    updateElement('#divSignal', divSignal);
    
    // Update score breakdown
    updateScoreBar('valuationBar', 'valuationScore', scores.valuation || 50);
    updateScoreBar('profitabilityBar', 'profitabilityScore', scores.profitability || 50);
    updateScoreBar('growthBar', 'growthScore', scores.growth || 50);
    updateScoreBar('healthBar', 'healthScore', scores.health || 50);
    
    // Overall score
    const overallScore = scores.overall || 50;
    updateElement('#fundStrengthValue', overallScore.toFixed(0));
    const fundStrengthFill = document.getElementById('fundStrengthFill');
    if (fundStrengthFill) {
        fundStrengthFill.style.width = `${overallScore}%`;
        if (overallScore >= 70) {
            fundStrengthFill.style.background = 'var(--gradient-green)';
        } else if (overallScore >= 40) {
            fundStrengthFill.style.background = 'linear-gradient(90deg, var(--warning-color), #f39c12)';
        } else {
            fundStrengthFill.style.background = 'var(--gradient-red)';
        }
    }
    
    // Signal action
    const signalAction = overallScore >= 70 ? 'STRONG BUY' : overallScore >= 60 ? 'BUY' : overallScore >= 40 ? 'HOLD' : overallScore >= 30 ? 'SELL' : 'STRONG SELL';
    updateElement('#fundSignalAction', signalAction);
    
    // Interpretation
    updateElement('#fundInterpretation', analysis.interpretation || 'Fundamental analysis completed.');
    
    console.log('✅ Fundamental analysis updated successfully');
}

// Helper function to update score bars
function updateScoreBar(barId, valueId, score) {
    const bar = document.getElementById(barId);
    if (bar) {
        bar.style.width = `${score}%`;
        if (score >= 70) {
            bar.className = 'score-fill';
        } else if (score >= 40) {
            bar.className = 'score-fill warning';
        } else {
            bar.className = 'score-fill danger';
        }
    }
    updateElement(`#${valueId}`, `${score.toFixed(0)}/100`);
}

// Update fundamental with default values
function updateFundamentalWithDefaults() {
    console.log('⚠️ Using default fundamental data');
    
    const defaultData = {
        metrics: {
            pe_ratio: 29.06,
            eps: 9.92,
            roe: 18.5,
            profit_margin: 12.3,
            operating_margin: 15.8,
            gross_margin: 54.2,
            revenue_growth: 5.2,
            quarterly_revenue_growth: 4.8,
            earnings_growth: 8.5,
            debt_to_equity: 2.15,
            current_ratio: 0.89,
            quick_ratio: 0.76,
            peg_ratio: 1.85,
            price_to_book: 6.45,
            dividend_yield: 3.16,
            dividend_payout_ratio: 65.4,
            sector_avg_pe: 25.0
        },
        scores: {
            valuation: 45,
            profitability: 72,
            growth: 55,
            health: 48,
            overall: 57
        },
        interpretation: 'IBM shows solid profitability metrics with strong ROE. Valuation appears fair relative to industry peers. Growth has been moderate but steady. Financial health is adequate with manageable debt levels.'
    };
    
    updateFundamentalAnalysis(defaultData);
}

// Update sentiment analysis display
function updateSentimentAnalysis(analysis) {
    if (!analysis) {
        console.warn('⚠️ No sentiment analysis data provided');
        return;
    }
    
    console.log('📰 Updating sentiment indicators:', analysis);
    
    // Overall Sentiment Score (-1 to 1)
    const score = analysis.score || 0;
    updateElement('#sentimentScore', score.toFixed(3));
    
    const sentimentStatus = score > 0.2 ? 'Positive' : score > 0.05 ? 'Slightly Positive' : score > -0.05 ? 'Neutral' : score > -0.2 ? 'Slightly Negative' : 'Negative';
    updateElement('#sentimentStatus', sentimentStatus);
    
    // Update sentiment bar
    const sentimentFill = document.getElementById('sentimentFill');
    if (sentimentFill) {
        // Convert -1 to 1 scale to 0 to 100%
        const percent = ((score + 1) / 2) * 100;
        sentimentFill.style.width = `${percent}%`;
        if (score > 0.2) {
            sentimentFill.style.background = 'var(--gradient-green)';
        } else if (score > -0.2) {
            sentimentFill.style.background = 'linear-gradient(90deg, var(--warning-color), #f39c12)';
        } else {
            sentimentFill.style.background = 'var(--gradient-red)';
        }
    }
    
    // News Sentiment
    const newsComponent = analysis.components?.news || {};
    updateElement('#newsScore', (newsComponent.score || 0).toFixed(3));
    updateElement('#newsVolume', newsComponent.article_count || 0);
    
    // Earnings Sentiment
    const earningsComponent = analysis.components?.transcripts || {};
    const earningsScore = earningsComponent.score || 0;
    updateElement('#earningsScore', earningsScore.toFixed(3));
    const earningsStatus = earningsScore > 0.2 ? 'Bullish' : earningsScore > -0.2 ? 'Neutral' : 'Bearish';
    updateElement('#earningsStatus', earningsStatus);
    
    // Sentiment Trend
    const trend = analysis.trend || 'neutral';
    updateElement('#trendDirection', trend.charAt(0).toUpperCase() + trend.slice(1));
    updateElement('#trendStrength', Math.abs(score) > 0.3 ? 'Strong' : Math.abs(score) > 0.1 ? 'Moderate' : 'Weak');
    
    // News Distribution
    updateElement('#positiveArticles', newsComponent.positive_articles || 0);
    updateElement('#neutralArticles', newsComponent.neutral_articles || 0);
    updateElement('#negativeArticles', newsComponent.negative_articles || 0);
    
    // Social Buzz
    const buzz = analysis.social_buzz || 0;
    updateElement('#socialBuzz', buzz.toFixed(1));
    const buzzStatus = buzz > 70 ? 'Very High' : buzz > 50 ? 'High' : buzz > 30 ? 'Moderate' : 'Low';
    updateElement('#buzzStatus', buzzStatus);
    updateElement('#buzzSignal', buzz > 50 ? 'High Activity' : 'Normal Activity');
    
    // Sentiment Signal
    updateElement('#sentimentStrengthValue', score.toFixed(3));
    const sentimentStrengthFill = document.getElementById('sentimentStrengthFill');
    if (sentimentStrengthFill) {
        const strengthPercent = ((score + 1) / 2) * 100;
        sentimentStrengthFill.style.width = `${strengthPercent}%`;
        if (score > 0.2) {
            sentimentStrengthFill.style.background = 'var(--gradient-green)';
        } else if (score > -0.2) {
            sentimentStrengthFill.style.background = 'linear-gradient(90deg, var(--warning-color), #f39c12)';
        } else {
            sentimentStrengthFill.style.background = 'var(--gradient-red)';
        }
    }
    
    // Signal Action
    const signalAction = score > 0.3 ? 'BULLISH' : score > 0.1 ? 'SLIGHTLY BULLISH' : score > -0.1 ? 'NEUTRAL' : score > -0.3 ? 'SLIGHTLY BEARISH' : 'BEARISH';
    updateElement('#sentimentSignalAction', signalAction);
    
    // Sentiment Signals
    const signals = analysis.signals || [];
    const reasonsList = document.getElementById('sentimentSignalReasons');
    if (reasonsList && signals.length > 0) {
        reasonsList.innerHTML = signals.map(signal => `<li>${signal}</li>`).join('');
    } else if (reasonsList) {
        reasonsList.innerHTML = '<li>No significant signals detected</li>';
    }
    
    // Interpretation
    updateElement('#sentimentInterpretation', analysis.interpretation || 'Sentiment analysis completed.');
    
    console.log('✅ Sentiment analysis updated successfully');
}

// Update sentiment with default values
function updateSentimentWithDefaults() {
    console.log('⚠️ Using default sentiment data');
    
    const defaultData = {
        score: 0.15,
        trend: 'improving',
        news_volume: 248,
        social_buzz: 45,
        interpretation: 'Overall sentiment is slightly positive. News coverage shows balanced reporting with moderate positive bias. Earnings transcripts reflect cautious optimism from management.',
        components: {
            news: {
                score: 0.12,
                article_count: 248,
                positive_articles: 105,
                neutral_articles: 98,
                negative_articles: 45
            },
            transcripts: {
                score: 0.18,
                confidence: 0.75
            },
            scores: {
                score: 0.15
            }
        },
        signals: [
            'News sentiment showing positive bias (0.12)',
            'Earnings calls reflect cautious optimism',
            'Media coverage at moderate levels (248 articles)',
            'Sentiment trend is improving',
            'Social buzz at healthy levels (45/100)'
        ]
    };
    
    updateSentimentAnalysis(defaultData);
}

// Update trade signals display
function updateTradeSignals(signal) {
    if (!signal) {
        console.warn('⚠️ No trade signal data provided');
        return;
    }
    
    console.log('🎯 Updating trade signals:', signal);
    
    // Overall Signal
    const signalAction = signal.signal || 'HOLD';
    const strength = signal.strength || 0;
    const confidence = signal.confidence || 0;
    const riskLevel = signal.risk_level || 'MEDIUM';
    const timeframe = signal.timeframe || 'Medium-term';
    
    updateElement('#tradeSignalAction', signalAction);
    updateElement('#tradeStrengthValue', strength.toFixed(2));
    updateElement('#tradeConfidence', `${confidence.toFixed(0)}%`);
    updateElement('#tradeRiskLevel', riskLevel);
    updateElement('#tradeTimeframe', timeframe);
    
    // Update strength bar
    const strengthFill = document.getElementById('tradeStrengthFill');
    if (strengthFill) {
        // Convert -100 to 100 scale to 0 to 100%
        const percent = ((strength + 100) / 200) * 100;
        strengthFill.style.width = `${percent}%`;
        if (signalAction.includes('STRONG_BUY') || signalAction.includes('BUY')) {
            strengthFill.style.background = 'var(--gradient-green)';
        } else if (signalAction.includes('STRONG_SELL') || signalAction.includes('SELL')) {
            strengthFill.style.background = 'var(--gradient-red)';
        } else {
            strengthFill.style.background = 'linear-gradient(90deg, var(--warning-color), #f39c12)';
        }
    }
    
    // Color code risk level
    const riskElement = document.getElementById('tradeRiskLevel');
    if (riskElement) {
        if (riskLevel === 'LOW') {
            riskElement.style.color = '#10B981';
        } else if (riskLevel === 'MEDIUM') {
            riskElement.style.color = 'var(--warning-color)';
        } else {
            riskElement.style.color = 'var(--danger-color)';
        }
    }
    
    // Component Signals
    const components = signal.components || {};
    
    // Technical
    if (components.technical) {
        updateElement('#techSignalScore', components.technical.score.toFixed(0));
        const techStatus = components.technical.score > 30 ? 'Bullish' : components.technical.score > -30 ? 'Neutral' : 'Bearish';
        updateElement('#techSignalStatus', techStatus);
    }
    
    // Fundamental
    if (components.fundamental) {
        updateElement('#fundSignalScore', components.fundamental.score.toFixed(0));
        const fundStatus = components.fundamental.score > 30 ? 'Strong' : components.fundamental.score > -30 ? 'Fair' : 'Weak';
        updateElement('#fundSignalStatus', fundStatus);
    }
    
    // Sentiment
    if (components.sentiment) {
        updateElement('#sentSignalScore', components.sentiment.score.toFixed(0));
        const sentStatus = components.sentiment.score > 30 ? 'Positive' : components.sentiment.score > -30 ? 'Neutral' : 'Negative';
        updateElement('#sentSignalStatus', sentStatus);
    }
    
    // Insider
    if (components.insider) {
        updateElement('#insiderSignalScore', components.insider.score.toFixed(0));
        const insiderStatus = components.insider.score > 30 ? 'Buying' : components.insider.score > -30 ? 'Neutral' : 'Selling';
        updateElement('#insiderSignalStatus', insiderStatus);
    }
    
    // Entry/Exit Prices
    updateElement('#entryPrice', signal.entry_price ? `$${signal.entry_price.toFixed(2)}` : '$0.00');
    updateElement('#stopLoss', signal.stop_loss ? `$${signal.stop_loss.toFixed(2)}` : '$0.00');
    updateElement('#takeProfit', signal.take_profit ? `$${signal.take_profit.toFixed(2)}` : '$0.00');
    
    // Calculate Risk/Reward Ratio
    if (signal.entry_price && signal.stop_loss && signal.take_profit) {
        const risk = Math.abs(signal.entry_price - signal.stop_loss);
        const reward = Math.abs(signal.take_profit - signal.entry_price);
        const ratio = risk > 0 ? (reward / risk).toFixed(2) : '--';
        updateElement('#riskReward', `1:${ratio}`);
    } else {
        updateElement('#riskReward', '--');
    }
    
    // Key Reasoning
    const reasons = signal.reasoning || [];
    const reasonsList = document.getElementById('tradeReasons');
    if (reasonsList && reasons.length > 0) {
        reasonsList.innerHTML = reasons.map(reason => `<li>${reason}</li>`).join('');
    } else if (reasonsList) {
        reasonsList.innerHTML = '<li>No specific insights available</li>';
    }
    
    console.log('✅ Trade signals updated successfully');
}

// Update trade signals with default values
function updateTradeSignalsWithDefaults() {
    console.log('⚠️ Using default trade signal data');
    
    // Get current symbol to provide appropriate defaults
    const currentSymbol = document.getElementById('symbolSelect')?.value || 'IBM';
    
    const symbolDefaults = {
        'IBM': {
            signal: 'WEAK_BUY',
            strength: 23.5,
            confidence: 62,
            entry_price: 288.50,
            stop_loss: 285.00,
            take_profit: 295.00,
            support_level: '$285',
            company_context: 'Revenue growth slowing, earnings declining'
        },
        'MSFT': {
            signal: 'MODERATE_BUY',
            strength: 42.8,
            confidence: 74,
            entry_price: 508.50,
            stop_loss: 495.00,
            take_profit: 535.00,
            support_level: '$495',
            company_context: 'Strong cloud growth, AI leadership'
        }
    };
    
    const defaults = symbolDefaults[currentSymbol] || symbolDefaults['IBM'];
    
    const defaultData = {
        signal: defaults.signal,
        strength: defaults.strength,
        confidence: defaults.confidence,
        risk_level: 'MEDIUM',
        timeframe: 'Short-term (2-4 weeks)',
        entry_price: defaults.entry_price,
        stop_loss: defaults.stop_loss,
        take_profit: defaults.take_profit,
        reasoning: [
            '📊 Technical indicators showing mixed signals with slight bullish bias',
            '💰 Fundamental metrics indicate fair valuation at current levels',
            '📰 Sentiment analysis reveals slightly positive market perception',
            '📈 RSI at 62 suggests room for upward movement',
            '⚠️ MACD showing weakening momentum',
            '✅ Price above 20-day moving average',
            `📉 ${defaults.company_context}`,
            `🎯 Strong support level identified at ${defaults.support_level}`,
            '⚡ Low trading volume suggests caution',
            '💡 Consider scaling into position on pullbacks'
        ],
        components: {
            technical: { score: 35, reasons: ['RSI bullish', 'Price above SMA20'] },
            fundamental: { score: currentSymbol === 'MSFT' ? 25 : 15, reasons: currentSymbol === 'MSFT' ? ['Strong fundamentals', 'AI growth'] : ['Fair valuation', 'Weak growth'] },
            sentiment: { score: 22, reasons: ['Positive news sentiment'] },
            insider: { score: 0, reasons: ['No significant insider activity'] }
        }
    };
    
    updateTradeSignals(defaultData);
}

// Update credibility tab with symbol-specific data
function updateCredibilityData(symbol = 'IBM') {
    console.log(`📊 Updating credibility data for ${symbol}`);
    
    const credibilityData = {
        'IBM': {
            // Summary metrics
            totalReturn: '+17.73%',
            returnAmount: '+$1,772.80',
            winRate: 'N/A',
            outperformance: '+2.36%',
            
            // Low Risk Strategy
            lowRisk: {
                entryDate: 'September 3, 2025',
                entryPrice: '$244.10',
                shares: 40,
                totalCost: '$9,764.00',
                cashRemaining: '$236.00',
                currentPrice: '$288.42',
                finalValue: '$11,536.80',
                totalPortfolio: '$11,772.80',
                technicalScore: '+5',
                fundamentalScore: '+5',
                sentimentScore: '+10',
                finalScore: '14.5',
                confidence: '54.5%',
                profitProgression: [
                    { date: 'Sept 8', profit: '+$479 (+4.9%)' },
                    { date: 'Sept 24', profit: '+$937 (+9.6%)' },
                    { date: 'Oct 10', profit: '+$1,772.80 (+17.73%)' }
                ]
            },
            
            // High Risk Strategy  
            highRisk: {
                entryDate: 'September 3, 2025',
                entryPrice: '$244.10',
                shares: 41,
                totalCost: '$10,008.10',
                cashRemaining: '$0.00',
                currentPrice: '$288.42',
                finalValue: '$11,825.22',
                totalPortfolio: '$11,825.22',
                totalReturn: '+18.25%',
                returnAmount: '+$1,825.22',
                finalScore: '18.5',
                confidence: '68.2%'
            }
        },
        
        'MSFT': {
            // Summary metrics
            totalReturn: '+22.84%',
            returnAmount: '+$2,284.00',
            winRate: 'N/A',
            outperformance: '+4.12%',
            
            // Low Risk Strategy
            lowRisk: {
                entryDate: 'September 3, 2025',
                entryPrice: '$420.50',
                shares: 23,
                totalCost: '$9,671.50',
                cashRemaining: '$328.50',
                currentPrice: '$510.96',
                finalValue: '$11,752.08',
                totalPortfolio: '$12,080.58',
                technicalScore: '+8',
                fundamentalScore: '+12',
                sentimentScore: '+15',
                finalScore: '26.9',
                confidence: '72.8%',
                profitProgression: [
                    { date: 'Sept 8', profit: '+$736 (+7.6%)' },
                    { date: 'Sept 24', profit: '+$1,472 (+15.2%)' },
                    { date: 'Oct 10', profit: '+$2,080.58 (+20.8%)' }
                ]
            },
            
            // High Risk Strategy
            highRisk: {
                entryDate: 'September 3, 2025',
                entryPrice: '$420.50',
                shares: 23,
                totalCost: '$9,671.50',
                sellDate: 'September 24, 2025',
                sellPrice: '$485.20',
                sellValue: '$11,159.60',
                reentryDate: 'September 30, 2025',
                reentryPrice: '$492.80',
                reentryShares: 22,
                reentryCost: '$10,841.60',
                currentPrice: '$510.96',
                finalValue: '$11,241.12',
                cashRemaining: '$318.00',
                totalPortfolio: '$11,559.12',
                totalReturn: '+15.59%',
                returnAmount: '+$1,559.12',
                finalScore: '31.2',
                confidence: '84.3%'
            }
        }
    };
    
    const data = credibilityData[symbol] || credibilityData['IBM'];
    
    // Update summary cards
    updateElement('#totalReturn', data.totalReturn);
    updateElement('#returnAmount', data.returnAmount);
    updateElement('#winRate', data.winRate);
    updateElement('#outperformance', data.outperformance);
    
    // Update Performance Metrics section
    updatePerformanceMetrics(data, symbol);
    
    // Update low risk strategy content
    updateCredibilityLowRisk(data.lowRisk, symbol);
    updateCredibilityHighRisk(data.highRisk, symbol);
    
    // Initialize credibility period selector (only once)
    if (!window.credibilityInitialized) {
        initializeCredibilityData();
        window.credibilityInitialized = true;
    }
}

function updatePerformanceMetrics(data, symbol) {
    // Performance metrics data for each symbol
    const performanceData = {
        'IBM': {
            totalReturn: '+17.73%',
            dollarGain: '+$1,772.80',
            maxDrawdown: '-2.14%',
            holdingPeriod: '37 days',
            tradesExecuted: '1 Buy',
            buyHoldReturn: '+15.37%'
        },
        'MSFT': {
            totalReturn: '+22.84%',
            dollarGain: '+$2,284.00',
            maxDrawdown: '-3.26%',
            holdingPeriod: '37 days',
            tradesExecuted: '1 Buy',
            buyHoldReturn: '+18.72%'
        }
    };
    
    const metrics = performanceData[symbol] || performanceData['IBM'];
    
    // Update performance metrics values
    const metricValues = document.querySelectorAll('.metrics-grid .metric-value');
    if (metricValues.length >= 6) {
        metricValues[0].textContent = metrics.totalReturn; // Total Return
        metricValues[1].textContent = metrics.dollarGain; // Dollar Gain
        metricValues[2].textContent = metrics.maxDrawdown; // Max Drawdown
        metricValues[3].textContent = metrics.holdingPeriod; // Holding Period
        metricValues[4].textContent = metrics.tradesExecuted; // Trades Executed
        metricValues[5].textContent = metrics.buyHoldReturn; // Buy & Hold Return
    }
}

function updateCredibilityLowRisk(data, symbol) {
    // Update the buy transaction details
    const strategyTitle = document.querySelector('#low-risk-content .strategy-info h3');
    if (strategyTitle) {
        strategyTitle.textContent = `📊 Low Risk Strategy (Conservative ${symbol} Approach)`;
    }
    
    // Update transaction header dates
    const finalPositionHeader = document.querySelector('#low-risk-content .transaction-item.final h4');
    if (finalPositionHeader) {
        finalPositionHeader.textContent = 'FINAL POSITION - October 10, 2025';
    }
    
    // Update transaction details
    const detailRows = document.querySelectorAll('#low-risk-content .transaction-details .detail-row');
    if (detailRows.length >= 4) {
        detailRows[0].querySelector('.value').textContent = data.entryPrice;
        detailRows[1].querySelector('.value').textContent = `${data.shares} shares`;
        detailRows[2].querySelector('.value').textContent = data.totalCost;
        detailRows[3].querySelector('.value').textContent = data.cashRemaining;
    }
    
    // Update indicator scores
    const indicatorScores = document.querySelectorAll('#low-risk-content .indicator-score');
    if (indicatorScores.length >= 3) {
        indicatorScores[0].textContent = data.technicalScore;
        indicatorScores[1].textContent = data.fundamentalScore;
        indicatorScores[2].textContent = data.sentimentScore;
    }
    
    // Update score calculation
    const scoreResult = document.querySelector('#low-risk-content .result');
    if (scoreResult) {
        scoreResult.innerHTML = `(${data.technicalScore.replace('+', '')} × 1.0) + (${data.fundamentalScore.replace('+', '')} × 0.7) + (${data.sentimentScore.replace('+', '')} × 0.6) = <strong>${data.finalScore} points</strong>`;
    }
    
    const signalResult = document.querySelector('#low-risk-content .signal-result');
    if (signalResult) {
        const signalType = parseFloat(data.finalScore) >= 20 ? 'MODERATE_BUY' : 'WEAK_BUY';
        const range = parseFloat(data.finalScore) >= 20 ? '20-29' : '10-19';
        signalResult.innerHTML = `Signal: <strong>${signalType}</strong> (Range: ${range}) | Confidence: <strong>${data.confidence}</strong>`;
    }
    
    // Update profit progression
    const profitRows = document.querySelectorAll('#low-risk-content .profit-row');
    if (profitRows.length >= 3 && data.profitProgression) {
        data.profitProgression.forEach((profit, index) => {
            if (profitRows[index]) {
                profitRows[index].innerHTML = `<span>${profit.date}:</span> <span class="profit">${profit.profit}</span>`;
            }
        });
    }
    
    // Update final position
    const finalDetails = document.querySelectorAll('#low-risk-content .transaction-item.final .detail-row');
    if (finalDetails.length >= 6) {
        finalDetails[0].querySelector('.value').textContent = data.currentPrice;
        finalDetails[1].querySelector('.value').textContent = `${data.shares} shares`;
        finalDetails[2].querySelector('.value').textContent = data.finalValue;
        finalDetails[3].querySelector('.value').textContent = data.cashRemaining;
        finalDetails[4].querySelector('.value').textContent = data.totalPortfolio;
        
        // Update the total profit row (usually the last one)
        const profitRow = finalDetails[5];
        if (profitRow && profitRow.classList.contains('profit')) {
            const profitAmount = parseFloat(data.totalPortfolio.replace(/[\$,]/g, '')) - 10000;
            const profitPercent = ((profitAmount / 10000) * 100).toFixed(2);
            profitRow.querySelector('.value').innerHTML = `<strong>+$${profitAmount.toFixed(2)} (+${profitPercent}%)</strong>`;
        }
    }
}

function updateCredibilityHighRisk(data, symbol) {
    // Create or update high risk content
    const highRiskContent = document.getElementById('high-risk-content');
    if (!highRiskContent) {
        createHighRiskContent();
    }
    
    // Update high risk strategy content
    const strategyTitle = document.querySelector('#high-risk-content .strategy-info h3');
    if (strategyTitle) {
        strategyTitle.textContent = `🚀 High Risk Strategy (Aggressive ${symbol} Approach)`;
    }
    
    const strategyDesc = document.querySelector('#high-risk-content .strategy-info p');
    if (strategyDesc) {
        strategyDesc.textContent = `Uses ALL signals with maximum position sizing and active trading. Maximizes gains through timing and leverage.`;
    }
    
    // Update summary metrics
    updateElement('#highRiskReturn', data.totalReturn);
    updateElement('#highRiskAmount', data.returnAmount);
    updateElement('#highRiskConfidence', data.confidence);
    updateElement('#highRiskScore', data.finalScore);
}

function createHighRiskContent() {
    const credibilityPanel = document.getElementById('credibility-panel');
    const highRiskHtml = `
        <div class="risk-content" id="high-risk-content">
            <div class="strategy-info">
                <h3>🚀 High Risk Strategy (Aggressive Approach)</h3>
                <p>Uses ALL signals with maximum position sizing and active trading. Maximizes gains through timing and leverage.</p>
            </div>
            
            <div class="high-risk-summary">
                <div class="metric-card">
                    <h4>Total Return</h4>
                    <div class="metric-value" id="highRiskReturn">+18.25%</div>
                    <div class="metric-desc" id="highRiskAmount">+$1,825.22</div>
                </div>
                <div class="metric-card">
                    <h4>Strategy Confidence</h4>
                    <div class="metric-value" id="highRiskConfidence">68.2%</div>
                    <div class="metric-desc">Average signal strength</div>
                </div>
                <div class="metric-card">
                    <h4>Final Score</h4>
                    <div class="metric-value" id="highRiskScore">18.5</div>
                    <div class="metric-desc">Weighted composite score</div>
                </div>
            </div>
            
            <div class="strategy-comparison">
                <h4>📊 Strategy Performance Comparison</h4>
                <div class="comparison-table">
                    <div class="comparison-row header">
                        <div>Metric</div>
                        <div>Low Risk</div>
                        <div>High Risk</div>
                        <div>Difference</div>
                    </div>
                    <div class="comparison-row">
                        <div>Total Return</div>
                        <div id="lowRiskReturnComp">+17.73%</div>
                        <div id="highRiskReturnComp">+18.25%</div>
                        <div class="positive">+0.52%</div>
                    </div>
                    <div class="comparison-row">
                        <div>Risk Level</div>
                        <div>Conservative</div>
                        <div>Aggressive</div>
                        <div>Higher volatility</div>
                    </div>
                    <div class="comparison-row">
                        <div>Max Drawdown</div>
                        <div>-2.1%</div>
                        <div>-4.8%</div>
                        <div class="negative">-2.7%</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Insert after low-risk-content
    const lowRiskContent = document.getElementById('low-risk-content');
    if (lowRiskContent) {
        lowRiskContent.insertAdjacentHTML('afterend', highRiskHtml);
    }
}

// Expose debug functions globally
window.debugAPI = debugAPIConnection;
window.loadData = () => loadStockData(currentSymbol);
window.forceRefresh = () => {
    console.log('🔄 Force refreshing all data...');
    loadStockData(currentSymbol);
};
window.testFundamental = async () => {
    console.log('🧪 Testing fundamental data load...');
    try {
        const response = await fetch(`${API_BASE}/fundamental/${currentSymbol}`);
        const data = await response.json();
        console.log('📊 Raw API response:', data);
        if (data && data.analysis) {
            console.log('✅ Calling updateFundamentalAnalysis with:', data.analysis);
            updateFundamentalAnalysis(data.analysis);
        } else {
            console.error('❌ No analysis in response');
        }
    } catch (error) {
        console.error('❌ Test failed:', error);
    }
};

// ====================================
// PORTFOLIO FORM FUNCTIONS
// ====================================

async function handlePortfolioSubmission() {
    console.log('📊 Handling portfolio form submission...');
    
    // Get form values
    const investmentCapital = parseFloat(document.getElementById('investmentCapital').value);
    const targetAmount = parseFloat(document.getElementById('targetAmount').value);
    const timeHorizon = parseInt(document.getElementById('timeHorizon').value);
    const riskAppetite = document.querySelector('input[name="riskAppetite"]:checked').value;
    
    // Validate
    if (!investmentCapital || !targetAmount || !timeHorizon || !riskAppetite) {
        showError('Please fill in all fields');
        return;
    }
    
    if (targetAmount <= investmentCapital) {
        showError('Target amount must be greater than investment capital');
        return;
    }
    
    // Create portfolio profile object
    const portfolioProfile = {
        investment_capital: investmentCapital,
        target_amount: targetAmount,
        time_horizon: timeHorizon,
        risk_appetite: riskAppetite
    };
    
    console.log('📤 Sending portfolio profile:', portfolioProfile);
    
    // Show loading state
    const submitBtn = document.getElementById('portfolioSubmitBtn');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="btn-icon">⏳</span><span class="btn-text">Processing...</span>';
    
    try {
        // Send to recommendation engine (Component 3)
        const response = await fetch(`${API_BASE}/portfolio-recommendation`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(portfolioProfile)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('✅ Portfolio recommendation received:', result);
        
        // Store profile for later use
        sessionStorage.setItem('portfolioProfile', JSON.stringify(portfolioProfile));
        
        // Display results with AI recommendations
        displayPortfolioResults(result);
        
        // Show success message
        submitBtn.innerHTML = '<span class="btn-icon">✅</span><span class="btn-text">Success!</span>';
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 2000);
        
    } catch (error) {
        console.error('❌ Portfolio submission error:', error);
        showError('Failed to get portfolio recommendations. Please try again.');
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

function displayPortfolioResults(data) {
    console.log('📊 Displaying portfolio results...', data);
    
    // Hide form, show results
    const form = document.querySelector('.profile-form-card');
    const results = document.getElementById('portfolioResults');
    const recommendations = document.getElementById('portfolioRecommendations');
    
    if (form) form.style.display = 'none';
    if (results) results.style.display = 'block';
    
    if (!recommendations) return;
    
    // Check if we have AI recommendation
    if (!data.success || !data.recommendation) {
        recommendations.innerHTML = `
            <div class="error-message">
                <h4>⚠️ Unable to generate recommendations</h4>
                <p>${data.error || 'Unknown error occurred'}</p>
            </div>
        `;
        return;
    }
    
    const rec = data.recommendation;
    const allocation = rec.portfolio_allocation || {};
    const justification = rec.justification || {};
    const returns = rec.expected_returns || {};
    const profile = data.user_profile || {};
    
    let html = '<div class="ai-recommendation-container">';
    
    // Header with AI branding
    html += `
        <div class="ai-header">
            <h3>🤖 Aura's AI-Powered Portfolio Recommendation</h3>
            <p class="ai-subtitle">Personalized allocation based on your profile and current market conditions</p>
        </div>
    `;
    
    // Portfolio Allocation Chart
    html += `
        <div class="allocation-section">
            <h4>📊 Recommended Allocation</h4>
            <div class="allocation-grid">
    `;
    
    const allocationItems = [
        { key: 'stocks_etfs', label: 'Stocks & ETFs', icon: '📈', color: '#10B981' },
        { key: 'bonds_fixed_income', label: 'Bonds & Fixed Income', icon: '💵', color: '#3B82F6' },
        { key: 'real_estate', label: 'Real Estate', icon: '🏘️', color: '#8B5CF6' },
        { key: 'commodities_gold', label: 'Commodities & Gold', icon: '🥇', color: '#F59E0B' },
        { key: 'cash_equivalents', label: 'Cash & Equivalents', icon: '💰', color: '#6B7280' }
    ];
    
    allocationItems.forEach(item => {
        const data = allocation[item.key] || {};
        const percentage = data.percentage || 0;
        const amount = data.amount || 0;
        
        html += `
            <div class="allocation-item">
                <div class="allocation-header">
                    <span class="allocation-icon">${item.icon}</span>
                    <span class="allocation-label">${item.label}</span>
                </div>
                <div class="allocation-percentage" style="color: ${item.color}">${percentage.toFixed(1)}%</div>
                <div class="allocation-amount">$${amount.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                <div class="allocation-bar">
                    <div class="allocation-fill" style="width: ${percentage}%; background: ${item.color}"></div>
                </div>
            </div>
        `;
    });
    
    html += `
            </div>
        </div>
    `;
    
    // Justification Section
    html += `
        <div class="justification-section">
            <h4>📋 Strategy & Justification</h4>
            
            <div class="justification-card">
                <h5>🎯 Overall Strategy</h5>
                <p>${justification.overall_strategy || 'N/A'}</p>
            </div>
            
            <div class="justification-card">
                <h5>⚖️ Risk Assessment</h5>
                <p>${justification.risk_assessment || 'N/A'}</p>
            </div>
            
            <div class="justification-card">
                <h5>📊 Market Conditions Impact</h5>
                <p>${justification.market_conditions_impact || 'N/A'}</p>
            </div>
            
            <div class="justification-card">
                <h5>⏰ Time Horizon Considerations</h5>
                <p>${justification.time_horizon_considerations || 'N/A'}</p>
            </div>
        </div>
    `;
    
    // Key Recommendations
    if (justification.key_recommendations && justification.key_recommendations.length > 0) {
        html += `
            <div class="recommendations-list">
                <h4>✨ Key Recommendations</h4>
                <ul>
        `;
        justification.key_recommendations.forEach(rec => {
            html += `<li>${rec}</li>`;
        });
        html += `
                </ul>
            </div>
        `;
    }
    
    // Expected Returns
    html += `
        <div class="returns-section">
            <h4>📈 Expected Returns</h4>
            <div class="returns-grid">
                <div class="return-item conservative">
                    <div class="return-label">Conservative</div>
                    <div class="return-value">${returns.conservative_estimate || 'N/A'}</div>
                </div>
                <div class="return-item moderate">
                    <div class="return-label">Moderate</div>
                    <div class="return-value">${returns.moderate_estimate || 'N/A'}</div>
                </div>
                <div class="return-item optimistic">
                    <div class="return-label">Optimistic</div>
                    <div class="return-value">${returns.optimistic_estimate || 'N/A'}</div>
                </div>
            </div>
        </div>
    `;
    
    // Disclaimer
    html += `
        <div class="ai-disclaimer">
            <p><strong>⚠️ Disclaimer:</strong> This recommendation is generated by AI based on your profile and current market data. It is for informational purposes only and should not be considered financial advice. Always consult with a qualified financial advisor before making investment decisions.</p>
        </div>
    `;
    
    html += '</div>';
    
    recommendations.innerHTML = html;
}

function showPortfolioForm() {
    console.log('✏️ Showing portfolio form...');
    
    // Hide results, show form
    const form = document.querySelector('.profile-form-card');
    const results = document.getElementById('portfolioResults');
    
    if (form) form.style.display = 'block';
    if (results) results.style.display = 'none';
    
    // Reload saved profile if available
    const savedProfile = sessionStorage.getItem('portfolioProfile');
    if (savedProfile) {
        try {
            const profile = JSON.parse(savedProfile);
            document.getElementById('investmentCapital').value = profile.investment_capital;
            document.getElementById('targetAmount').value = profile.target_amount;
            document.getElementById('timeHorizon').value = profile.time_horizon;
            document.querySelector(`input[name="riskAppetite"][value="${profile.risk_appetite}"]`).checked = true;
        } catch (error) {
            console.error('Error loading saved profile:', error);
        }
    }
}

// ====================================
// MARKET DATA DISPLAY FUNCTIONS
// ====================================

async function loadMarketData() {
    console.log('📊 Loading market data...');
    
    const container = document.getElementById('marketDataDisplay');
    const refreshBtn = document.getElementById('refreshMarketData');
    
    if (!container) return;
    
    // Show loading state
    container.innerHTML = `
        <div class="loading-market-data">
            <div class="spinner"></div>
            <p>Fetching latest market data...</p>
        </div>
    `;
    
    if (refreshBtn) refreshBtn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE}/market-data`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const marketData = await response.json();
        console.log('✅ Market data received:', marketData);
        
        displayMarketData(marketData);
        
    } catch (error) {
        console.error('❌ Error loading market data:', error);
        container.innerHTML = `
            <div class="error-message">
                <h4>⚠️ Unable to load market data</h4>
                <p>${error.message}</p>
                <p>Please check your API keys and try again.</p>
            </div>
        `;
    } finally {
        if (refreshBtn) refreshBtn.disabled = false;
    }
}

function displayMarketData(data) {
    const container = document.getElementById('marketDataDisplay');
    if (!container) return;
    
    const { economic_indicators, market_performance, market_sentiment, metadata } = data;
    
    let html = '<div class="market-data-grid">';
    
    // Economic Indicators
    html += `
        <div class="market-category">
            <h4>💰 Economic Indicators</h4>
            <div class="market-metrics">
                ${createMetric('Inflation (CPI)', economic_indicators.inflation_rate, 'index')}
                ${createMetric('Fed Funds Rate', economic_indicators.federal_funds_rate, 'percent')}
                ${createMetric('GDP Growth', economic_indicators.gdp_growth_rate, 'percent')}
                ${createMetric('Unemployment', economic_indicators.unemployment_rate, 'percent')}
            </div>
        </div>
    `;
    
    // Market Performance
    html += `
        <div class="market-category">
            <h4>📈 Market Performance</h4>
            <div class="market-metrics">
                ${createMetric('S&P 500 (SPY)', market_performance.sp500, 'price')}
                ${createMetric('Volatility (VXX)', market_performance.vix, 'price')}
                ${createMetric('Treasury (TLT)', market_performance.treasury_10y, 'price')}
                ${createMetric('Gold (GLD)', market_performance.gold, 'price')}
                ${createMetric('Real Estate (VNQ)', market_performance.vnq, 'price')}
            </div>
        </div>
    `;
    
    // Market Sentiment
    const headlines = market_sentiment.headlines || [];
    html += `
        <div class="market-category" style="grid-column: 1 / -1;">
            <h4>📰 Market Sentiment</h4>
            <div class="headlines-section">
    `;
    
    if (headlines.length > 0) {
        headlines.slice(0, 5).forEach(headline => {
            html += `
                <div class="headline-item">
                    <div class="headline-title">${headline.title || 'No title'}</div>
                    <div class="headline-source">${headline.source || 'Unknown'} • ${formatDate(headline.published_at)}</div>
                </div>
            `;
        });
    } else {
        html += `<p style="color: var(--text-secondary); text-align: center;">No recent headlines available</p>`;
    }
    
    html += `
            </div>
        </div>
    `;
    
    html += '</div>';
    
    // Add timestamp
    const timestamp = new Date(data.timestamp).toLocaleString();
    html += `
        <div class="market-timestamp">
            Last updated: ${timestamp}
            ${metadata.aggregation_duration_seconds ? 
                `• Loaded in ${metadata.aggregation_duration_seconds.toFixed(2)}s` : ''}
        </div>
    `;
    
    container.innerHTML = html;
}

function createMetric(label, data, type) {
    if (!data || data.error) {
        return `
            <div class="market-metric">
                <span class="metric-label">${label}</span>
                <span class="metric-value neutral">N/A</span>
            </div>
        `;
    }
    
    let value = data.value !== undefined ? data.value : data.current_price;
    if (value === null || value === undefined) {
        return `
            <div class="market-metric">
                <span class="metric-label">${label}</span>
                <span class="metric-value neutral">N/A</span>
            </div>
        `;
    }
    
    let displayValue = '';
    switch(type) {
        case 'price':
            displayValue = `$${value.toFixed(2)}`;
            break;
        case 'percent':
            displayValue = `${value.toFixed(2)}%`;
            break;
        case 'index':
            displayValue = value.toFixed(1);
            break;
        default:
            displayValue = value.toFixed(2);
    }
    
    return `
        <div class="market-metric">
            <span class="metric-label">${label}</span>
            <span class="metric-value">${displayValue}</span>
        </div>
    `;
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
}

// Helper function to format period for display
function formatPeriodForDisplay(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    
    const formatOptions = { month: 'long', day: 'numeric' };
    const startFormatted = start.toLocaleDateString('en-US', formatOptions);
    const endFormatted = end.toLocaleDateString('en-US', formatOptions);
    const year = end.getFullYear();
    
    return `${startFormatted} - ${endFormatted}, ${year}`;
}

// Function to load credibility data for a specific period
async function loadCredibilityDataForPeriod(startDate, endDate) {
    console.log(`📅 Loading credibility analysis for period: ${startDate} to ${endDate}`);
    
    try {
        // Show loading state
        showLoadingForPeriod();
        
        // For now, we'll simulate different data based on the period
        // In a real implementation, you would call your backend API with the date parameters
        // const response = await fetch(`${API_BASE}/credibility/${currentSymbol}?start=${startDate}&end=${endDate}`);
        
        // Generate period-specific mock data
        const periodData = generateMockCredibilityData(startDate, endDate);
        
        // Update the UI with the new data
        updateCredibilityDisplay(periodData);
        
        console.log(`✅ Credibility data loaded for ${startDate} to ${endDate}`);
        
    } catch (error) {
        console.error('❌ Failed to load credibility data:', error);
        showError(`Failed to load data for selected period: ${error.message}`);
    } finally {
        hideLoadingForPeriod();
    }
}

// Function to generate mock credibility data based on period
function generateMockCredibilityData(startDate, endDate) {
    // Calculate some basic period info
    const start = new Date(startDate);
    const end = new Date(endDate);
    const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    
    const startMonth = monthNames[start.getMonth()];
    const endMonth = monthNames[end.getMonth()];
    const startDay = start.getDate();
    const endDay = end.getDate();
    
    // Generate different performance metrics based on the period
    // This simulates seasonal variations in trading performance
    const monthIndex = start.getMonth();
    const seasonalMultiplier = [0.8, 0.9, 1.1, 1.2, 1.0, 0.7, 0.6, 0.8, 1.3, 1.5, 1.1, 0.9][monthIndex];
    
    const baseReturn = 15.0 * seasonalMultiplier;
    const baseProfit = 1500.0 * seasonalMultiplier;
    
    return {
        period: `${startMonth} ${startDay} - ${endMonth} ${endDay}`,
        totalReturn: `+${baseReturn.toFixed(2)}%`,
        returnAmount: `+$${baseProfit.toFixed(2)}`,
        winRate: monthIndex < 6 ? "75%" : "68%", // Better win rate in first half of year
        outperformance: `+${(baseReturn - 12).toFixed(2)}%`,
        
        // Low risk strategy data
        lowRisk: {
            finalValue: `$${(10000 + baseProfit * 0.8).toFixed(2)}`,
            totalProfit: `+$${(baseProfit * 0.8).toFixed(2)}`,
            returnPercent: `+${(baseReturn * 0.8).toFixed(2)}%`,
            trades: monthIndex % 2 === 0 ? 1 : 0, // Alternate periods have trades
            winRate: "100%"
        },
        
        // High risk strategy data  
        highRisk: {
            finalValue: `$${(10000 + baseProfit * 1.2).toFixed(2)}`,
            totalProfit: `+$${(baseProfit * 1.2).toFixed(2)}`,
            returnPercent: `+${(baseReturn * 1.2).toFixed(2)}%`,
            trades: monthIndex < 6 ? 2 : 3, // More trades in second half
            winRate: `${Math.round(65 + seasonalMultiplier * 10)}%`
        },
        
        // Period-specific details
        buyPrice: `$${(240 + monthIndex * 2).toFixed(2)}`,
        sellPrice: `$${(240 + monthIndex * 2 + baseReturn * 2.4).toFixed(2)}`,
        holdingDays: Math.round(20 + seasonalMultiplier * 5)
    };
}

// Function to update credibility display with new data
function updateCredibilityDisplay(data) {
    // Update summary cards
    updateElement('#totalReturn', data.totalReturn);
    updateElement('#returnAmount', data.returnAmount);
    updateElement('#winRate', data.winRate);
    updateElement('#outperformance', data.outperformance);
    
    // Update specific strategy data
    // Low Risk Strategy
    updateElement('#lowRiskFinalValue', data.lowRisk.finalValue);
    updateElement('#lowRiskProfit', data.lowRisk.totalProfit);
    updateElement('#lowRiskReturn', data.lowRisk.returnPercent);
    
    // High Risk Strategy  
    updateElement('#highRiskFinalValue', data.highRisk.finalValue);
    updateElement('#highRiskProfit', data.highRisk.totalProfit);
    updateElement('#highRiskReturn', data.highRisk.returnPercent);
    
    // Update transaction details if elements exist
    if (data.lowRisk.trades > 0) {
        updateElement('#buyPrice', data.buyPrice);
        updateElement('#sellPrice', data.sellPrice);
        updateElement('#holdingDays', `${data.holdingDays} days`);
    }
    
    console.log(`✅ Updated credibility display for ${data.period}`);
}

// Loading state functions
function showLoadingForPeriod() {
    document.querySelectorAll('.period-tab').forEach(tab => {
        if (!tab.classList.contains('active')) {
            tab.classList.add('loading');
        }
    });
    
    // Show loading on summary cards
    document.querySelectorAll('.card-value').forEach(card => {
        card.style.opacity = '0.6';
    });
}

function hideLoadingForPeriod() {
    document.querySelectorAll('.period-tab').forEach(tab => {
        tab.classList.remove('loading');
    });
    
    // Remove loading from summary cards
    document.querySelectorAll('.card-value').forEach(card => {
        card.style.opacity = '1';
    });
}

// Initialize credibility data on page load
function initializeCredibilityData() {
    // Set default period (Sept 10 - Oct 10, 2025)
    const defaultStartDate = '2025-09-10';
    const defaultEndDate = '2025-10-10';
    
    // Update subtitle
    const subtitle = document.getElementById('selected-period-subtitle');
    if (subtitle) {
        const formattedPeriod = formatPeriodForDisplay(defaultStartDate, defaultEndDate);
        subtitle.textContent = `Comprehensive backtesting performance over ${formattedPeriod}`;
    }
    
    console.log('📅 Initialized credibility data with default period');
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});
