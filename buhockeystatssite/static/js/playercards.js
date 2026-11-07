// Player Cards: a game card (every BU player in one game) or a player card
// (career by season, or one season game by game), drawn as stacked GameScore bars.

const IC_PARTS = ['Production', 'Misc', 'Offense', 'Defense'];
const IC_COLORS = ['#fdcab5', '#fc8a6a', '#f14432', '#bc141a'];   // matplotlib Reds, same as plot_game_card

const icView = document.getElementById('icView');
const icGameSeason = document.getElementById('icGameSeason');
const icGame = document.getElementById('icGame');
const icPlayer = document.getElementById('icPlayer');
const icPlayerSeason = document.getElementById('icPlayerSeason');
const icChart = document.getElementById('icChart');
const icTooltip = document.getElementById('icTooltip');
const icSort = document.getElementById('icSort');
const icShowEx = document.getElementById('icShowEx');
const icAscending = document.getElementById('icAscending');

let icCurrentRows = [];      // rows of the card being shown (redrawn when the window is resized)

// ---------------------------------------------------------------- helpers
function fillSelect(select, options, selected) {
    select.innerHTML = '';
    options.forEach(function (opt) {
        const o = document.createElement('option');
        o.value = opt.value;
        o.textContent = opt.text;
        select.appendChild(o);
    });
    if (selected !== undefined && options.some(o => String(o.value) === String(selected))) {
        select.value = selected;
    }
}

function unique(list) {
    return list.filter((v, i) => list.indexOf(v) === i);
}

function fmt(v) {
    return (v >= 0 ? '' : '−') + Math.abs(v).toFixed(2);
}

function niceStep(range) {
    const rough = range / 6;
    const pow = Math.pow(10, Math.floor(Math.log10(rough)));
    for (const m of [1, 2, 2.5, 5, 10]) {
        if (rough <= m * pow) return m * pow;
    }
    return 10 * pow;
}

// averages of the four parts and the total over several games
function averageRow(label, rows, tip) {
    const sums = [0, 0, 0, 0, 0];
    rows.forEach(r => { for (let k = 0; k < 5; k++) sums[k] += r[2 + k]; });
    const n = rows.length;
    return { label: label, parts: sums.slice(0, 4).map(s => s / n), total: sums[4] / n, tip: tip };
}

// ---------------------------------------------------------------- drawing
// pixel widths of labels in the card's label font
function measureLabels(labels) {
    const svgNS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('class', 'impact-svg');
    svg.style.position = 'absolute';
    svg.style.visibility = 'hidden';
    const text = document.createElementNS(svgNS, 'text');
    text.setAttribute('class', 'impact-label');
    svg.appendChild(text);
    document.body.appendChild(svg);
    const widths = labels.map(function (l) { text.textContent = l; return text.getComputedTextLength(); });
    svg.remove();
    return widths.length ? widths : [0];
}

// one line if the label fits, otherwise two lines split at the space nearest the middle
function splitLabel(label, maxW) {
    if (measureLabels([label])[0] <= maxW) return [label];
    const words = label.split(' ');
    if (words.length < 2) return [label];
    let best = null;
    for (let k = 1; k < words.length; k++) {
        const a = words.slice(0, k).join(' '), b = words.slice(k).join(' ');
        const w = Math.max.apply(null, measureLabels([a, b]));
        if (best === null || w < best.w) best = { lines: [a, b], w: w };
    }
    return best.lines;
}

function drawCard(rows, emptyMessage) {
    icCurrentRows = rows;
    document.getElementById('icSaveButton').hidden = !rows.length;
    if (!rows.length) {
        icChart.innerHTML = '<p class="impact-empty">' + (emptyMessage || 'No GameScore data for this selection.') + '</p>';
        return;
    }
    const svgNS = 'http://www.w3.org/2000/svg';
    const width = Math.max(icChart.clientWidth, 280);
    const narrow = width < 520;
    const totalW = narrow ? 46 : 60;
    const minPlotW = narrow ? 130 : 300;

    // size the name column to the longest label; if that would squeeze the bars too much,
    // cap the column and put long labels on two lines
    const longest = Math.max.apply(null, measureLabels(rows.map(r => r.label)));
    const maxLabelW = width - totalW - minPlotW;
    const labelW = Math.max(60, Math.min(longest + 16, maxLabelW));
    const lines = rows.map(r => splitLabel(r.label, labelW - 12));
    const twoLine = lines.some(l => l.length > 1);
    const rowH = twoLine ? (narrow ? 34 : 38) : (narrow ? 24 : 28);
    const top = 22, bottom = 34;
    const plotW = width - labelW - totalW;
    const height = top + rows.length * rowH + bottom;

    // x range: negatives stack left of 0, positives right (like the pandas stacked bar)
    let lo = 0, hi = 0;
    rows.forEach(r => {
        let pos = 0, neg = 0;
        r.parts.forEach(v => { if (v >= 0) pos += v; else neg += v; });
        hi = Math.max(hi, pos);
        lo = Math.min(lo, neg);
    });
    const step = niceStep((hi - lo) || 1);
    lo = Math.floor(lo / step) * step;
    hi = Math.ceil(hi / step) * step;
    if (hi === lo) hi = lo + step;
    const x = v => labelW + (v - lo) / (hi - lo) * plotW;

    const svg = document.createElementNS(svgNS, 'svg');
    svg.setAttribute('width', width);
    svg.setAttribute('height', height);
    svg.setAttribute('class', 'impact-svg');
    const add = (tag, attrs, text) => {
        const el = document.createElementNS(svgNS, tag);
        for (const a in attrs) el.setAttribute(a, attrs[a]);
        if (text !== undefined) el.textContent = text;
        svg.appendChild(el);
        return el;
    };

    // grid lines and x-axis labels
    for (let t = lo; t <= hi + step / 2; t += step) {
        const tx = x(t);
        const zero = Math.abs(t) < step / 1000;
        add('line', { x1: tx, x2: tx, y1: top - 4, y2: top + rows.length * rowH,
                      stroke: zero ? '#999' : '#e6e6e6', 'stroke-width': zero ? 1.2 : 0.8 });
        add('text', { x: tx, y: top + rows.length * rowH + 16, 'text-anchor': 'middle', class: 'impact-tick' },
            (Math.round(t * 100) / 100).toString());
    }
    add('text', { x: labelW + plotW / 2, y: height - 4, 'text-anchor': 'middle', class: 'impact-axis' },
        'GameScore Composition');
    add('text', { x: labelW + plotW + 8, y: top - 8, class: 'impact-total-head' }, 'Total');

    rows.forEach(function (r, i) {
        const y0 = top + i * rowH;
        const barY = y0 + rowH * 0.1, barH = rowH * 0.8;
        const parts = lines[i];
        const label = add('text', { x: labelW - 8, y: y0 + rowH / 2, 'text-anchor': 'end',
                                    'dominant-baseline': 'central', class: 'impact-label' });
        parts.forEach(function (line, j) {
            const t = document.createElementNS(svgNS, 'tspan');
            t.setAttribute('x', labelW - 8);
            // two lines sit just above and below the middle of the row
            t.setAttribute('dy', parts.length === 1 ? '0' : (j === 0 ? '-0.55em' : '1.1em'));
            t.textContent = line;
            label.appendChild(t);
        });
        let pos = 0, neg = 0;
        r.parts.forEach(function (v, k) {
            let a, b;
            if (v >= 0) { a = pos; b = pos + v; pos = b; } else { a = neg + v; b = neg; neg = a; }
            if (b - a <= 0) return;
            add('rect', { x: x(a), y: barY, width: Math.max(x(b) - x(a), 0.5), height: barH, fill: IC_COLORS[k] });
        });
        add('text', { x: labelW + plotW + 8, y: y0 + rowH / 2, 'dominant-baseline': 'central',
                      class: 'impact-total' }, r.total.toFixed(2));
        // invisible full-row target for the hover / tap breakdown
        const hit = add('rect', { x: 0, y: y0, width: width, height: rowH, fill: 'transparent', class: 'impact-hit' });
        hit.addEventListener('mousemove', e => showTip(e, r));
        hit.addEventListener('click', e => showTip(e, r));
        hit.addEventListener('mouseleave', hideTip);
    });
    // swap the new chart in, in one step: emptying the box first would shrink the page for a moment,
    // and phones then jump the scroll position back to the top
    icChart.replaceChildren(svg);
}

function showTip(e, r) {
    let html = '<div class="impact-tip-title">' + r.tip + '</div>';
    r.parts.forEach(function (v, k) {
        html += '<div><i style="background:' + IC_COLORS[k] + '"></i>' + IC_PARTS[k] + ': <b>' + fmt(v) + '</b></div>';
    });
    html += '<div class="impact-tip-total">Total: <b>' + fmt(r.total) + '</b></div>';
    icTooltip.innerHTML = html;
    icTooltip.hidden = false;
    const pad = 14;
    let left = e.clientX + pad, topPos = e.clientY + pad;
    const w = icTooltip.offsetWidth, h = icTooltip.offsetHeight;
    if (left + w > window.innerWidth - 8) left = e.clientX - w - pad;
    if (topPos + h > window.innerHeight - 8) topPos = e.clientY - h - pad;
    icTooltip.style.left = Math.max(8, left) + 'px';
    icTooltip.style.top = Math.max(8, topPos) + 'px';
}

function hideTip() {
    icTooltip.hidden = true;
}

// ---------------------------------------------------------------- save as PNG
// Rebuilds the card (title, chart, legend, credit) as one SVG image and draws it onto a canvas.
const IC_EXPORT_CSS = `
  text { font-family: 'Quicksand', 'Segoe UI', Arial, sans-serif; }
  .impact-label { font-size: 13px; fill: #222222; }
  .impact-tick { font-size: 11px; fill: #555555; }
  .impact-axis { font-size: 13px; fill: #222222; }
  .impact-total { font-size: 13px; font-weight: 700; fill: black; }
  .impact-total-head { font-size: 11px; font-weight: 700; fill: #666666; }
  .t-title { font-size: 22px; font-weight: 700; fill: #222222; }
  .t-sub { font-size: 14px; fill: #666666; }
  .t-legend { font-size: 12px; fill: #333333; }
  .t-credit { font-size: 11px; fill: #777777; }`;

function escapeXml(text) {
    return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// The saved image is drawn from an SVG, and an SVG drawn as an image can't use the page's web fonts,
// so the Quicksand font file (the same one layout.html loads from Google Fonts) is put inside the SVG.
const IC_FONT_CSS_URL = 'https://fonts.googleapis.com/css2?family=Quicksand';
let icFontFace = null;

async function embeddedFontFace() {
    if (icFontFace !== null) return icFontFace;
    try {
        const css = await (await fetch(IC_FONT_CSS_URL)).text();
        // Google splits the font by character set; use the Latin part (plain letters, digits, dashes)
        const faces = css.split('@font-face').filter(f => f.includes('url('));
        const latin = faces.find(f => /U\+0000-00FF/.test(f)) || faces[faces.length - 1];
        const url = latin.match(/url\(([^)]+)\)/)[1].replace(/['"]/g, '');
        const blob = await (await fetch(url)).blob();
        const dataUrl = await new Promise(function (resolve, reject) {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsDataURL(blob);
        });
        icFontFace = "@font-face { font-family: 'Quicksand'; src: url(" + dataUrl + ") format('woff2'); }";
    } catch (e) {
        icFontFace = '';        // couldn't get the font: the image falls back to a standard font
    }
    return icFontFace;
}

async function saveCardPNG() {
    const chart = icChart.querySelector('svg');
    if (!chart) return;
    const chartW = Number(chart.getAttribute('width'));
    const chartH = Number(chart.getAttribute('height'));
    const pad = 20;
    const W = chartW + pad * 2;
    const legendTexts = ['Production: Player points and individual actions', 'Misc: Includes penalties drawn, faceoffs, etc.',
                         'Offense: Offensive impact above average', 'Defense: Defensive impact above average'];
    const legendCols = chartW >= 520 ? 2 : 1;
    const legendH = Math.ceil(4 / legendCols) * 20;
    const top = 78;
    const H = top + chartH + 14 + legendH + 34;

    let body = '<rect width="' + W + '" height="' + H + '" fill="#fffafa"/>';
    body += '<rect x="6" y="6" width="' + (W - 12) + '" height="' + (H - 12) + '" rx="14" fill="white" stroke="#cccccc"/>';
    body += '<text class="t-title" x="' + W / 2 + '" y="38" text-anchor="middle">' + escapeXml(document.getElementById('icTitle').textContent) + '</text>';
    body += '<text class="t-sub" x="' + W / 2 + '" y="62" text-anchor="middle">' + escapeXml(document.getElementById('icSubtitle').textContent) + '</text>';
    body += '<g transform="translate(' + pad + ',' + top + ')">' + chart.innerHTML + '</g>';
    const ly = top + chartH + 14;
    legendTexts.forEach(function (t, k) {
        const col = k % legendCols, row = Math.floor(k / legendCols);
        const x = pad + 10 + col * (chartW / legendCols), y = ly + row * 20;
        body += '<rect x="' + x + '" y="' + y + '" width="12" height="12" fill="' + IC_COLORS[k] + '"/>';
        body += '<text class="t-legend" x="' + (x + 18) + '" y="' + (y + 10) + '">' + escapeXml(t) + '</text>';
    });
    body += '<text class="t-credit" x="' + W / 2 + '" y="' + (H - 18) + '" text-anchor="middle">' +
            'Plot: @BUHockeyStats  |  Stat Card inspired by @hockeystatcards  |  GameScore: @domluszczyszyn  |  Data: Instat</text>';
    const fontFace = await embeddedFontFace();
    const svgText = '<svg xmlns="http://www.w3.org/2000/svg" width="' + W + '" height="' + H + '"><style>' +
                    fontFace + IC_EXPORT_CSS + '</style>' + body + '</svg>';

    const scale = 2;                                     // sharper image
    const img = new Image();
    img.onload = () => setTimeout(function () {      // short pause so the embedded font is ready in every browser
        const canvas = document.createElement('canvas');
        canvas.width = W * scale;
        canvas.height = H * scale;
        const ctx = canvas.getContext('2d');
        ctx.scale(scale, scale);
        ctx.drawImage(img, 0, 0);
        canvas.toBlob(function (blob) {
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = cardFileName();
            document.body.appendChild(a);
            a.click();
            a.remove();
            setTimeout(() => URL.revokeObjectURL(a.href), 1000);
        }, 'image/png');
    }, 60);
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgText);
}

function cardFileName() {
    let name;
    if (icView.value === 'game') {
        const g = IC_GAMES[Number(icGame.value)];
        name = 'BU_ImpactCard_' + g.date + '_' + g.short.slice(6);
    } else {
        name = icPlayer.value + '_' + (icPlayerSeason.value === 'career' ? 'Career' : icPlayerSeason.value) + '_ImpactCard';
    }
    return name.replace(/[^A-Za-z0-9_\-]+/g, '_') + '.png';
}

// exhibitions only show when the Exhibitions switch is on
function gameShown(gameIndex) {
    return icShowEx.checked || IC_GAMES[gameIndex].result !== 'Exhibition';
}

// ---------------------------------------------------------------- sorting
// rows marked `pinned` always stay at the bottom
function sortRows(rows) {
    const key = icSort.value;
    const asc = icAscending.value === 'true';
    const value = function (r) {
        if (key === 'date') return r.order;
        if (key === 'name') return r.label;
        if (key === 'total') return r.total;
        return r.parts[Number(key)];
    };
    const body = rows.filter(r => !r.pinned);
    body.sort(function (a, b) {
        const va = value(a), vb = value(b);
        const c = (typeof va === 'string') ? va.localeCompare(vb) : va - vb;
        return asc ? c : -c;
    });
    return body.concat(rows.filter(r => r.pinned));
}

function showArrows() {
    const asc = icAscending.value === 'true';
    document.getElementById('icArrowUp').style.display = asc ? 'inline-block' : 'none';
    document.getElementById('icArrowDown').style.display = asc ? 'none' : 'inline-block';
}

function toggleImpactArrow() {
    icAscending.value = icAscending.value === 'true' ? 'false' : 'true';
    showArrows();
    showCard();
}

// default sort for each view: game card by total (best first), player card by date (oldest first)
function setDefaultSort() {
    const isGame = icView.value === 'game';
    icSort.value = isGame ? 'total' : 'date';
    icAscending.value = isGame ? 'false' : 'true';
    document.querySelectorAll('#icSort .player-sort').forEach(o => { o.hidden = isGame; o.disabled = isGame; });
    document.querySelectorAll('#icSort .game-sort').forEach(o => { o.hidden = !isGame; o.disabled = !isGame; });
    showArrows();
}

// ---------------------------------------------------------------- cards
function setTitle(title, subtitle) {
    document.getElementById('icTitle').textContent = title;
    document.getElementById('icSubtitle').textContent = subtitle;
}

function showGameCard() {
    const g = Number(icGame.value);
    const game = IC_GAMES[g];
    if (!game) { setTitle('', ''); drawCard([]); return; }
    const rows = IC_ROWS.filter(r => r[0] === g)
        .map(r => ({ label: r[1], parts: r.slice(2, 6), total: r[6], tip: r[1] }));
    setTitle('BU Player Impact Game Card', game.label + (game.result ? '  (' + game.result + ')' : ''));
    drawCard(sortRows(rows));
}

function showPlayerCard() {
    const player = icPlayer.value;
    const season = icPlayerSeason.value;
    if (!player) {
        setTitle('', '');
        drawCard([], 'Select a player to see their impact card.');
        return;
    }
    const mine = IC_ROWS.filter(r => r[1] === player && gameShown(r[0]));
    if (!mine.length) { setTitle('', ''); drawCard([]); return; }
    const career = season === 'career';
    // one bar per game: the whole career, or one season
    const games = (career ? mine : mine.filter(r => IC_GAMES[r[0]].season === season)).sort((a, b) => a[0] - b[0]);
    const rows = games.map(function (r) {
        const g = IC_GAMES[r[0]];
        // the career card spans several seasons, so its labels carry the year
        const label = career ? g.date.slice(5, 7) + '/' + g.date.slice(8, 10) + '/' + g.date.slice(2, 4) + g.short.slice(5) : g.short;
        return { label: label, parts: r.slice(2, 6), total: r[6], order: r[0],
                 tip: g.label + (g.result ? ' (' + g.result + ')' : '') };
    });
    const avg = averageRow('', games, '');
    setTitle(player + ' – ' + (career ? 'Career' : season) + ' Impact Card',
             games.length + ' GP  |  Average GameScore ' + avg.total.toFixed(2));
    drawCard(sortRows(rows));
}

// ---------------------------------------------------------------- dropdowns
function updateGameList(keepGame) {
    const season = icGameSeason.value;
    const options = [];
    IC_GAMES.forEach(function (game, i) {
        if ((season === 'all' || game.season === season) && gameShown(i)) options.push({ value: i, text: game.label });  // oldest first
    });
    // keep the chosen game if it's still in the list, otherwise show the most recent game
    const keep = options.some(o => String(o.value) === String(keepGame)) ? keepGame : (options.length ? options[options.length - 1].value : undefined);
    fillSelect(icGame, options, keep);
}

function updatePlayerSeasons() {
    if (!icPlayer.value) {                      // no player chosen yet: nothing to pick a season for
        fillSelect(icPlayerSeason, []);
        icPlayerSeason.disabled = true;
        return;
    }
    icPlayerSeason.disabled = false;
    const seasons = unique(IC_ROWS.filter(r => r[1] === icPlayer.value && gameShown(r[0])).map(r => IC_GAMES[r[0]].season)).sort();     // oldest first
    const prev = icPlayerSeason.value;
    fillSelect(icPlayerSeason, [{ value: 'career', text: 'Career' }].concat(seasons.map(s => ({ value: s, text: s }))), prev);
}

function showCard() {
    hideTip();
    if (icView.value === 'game') showGameCard(); else showPlayerCard();
}

function showView() {
    const isGame = icView.value === 'game';
    document.querySelectorAll('.game-filter').forEach(el => { el.hidden = !isGame; });
    document.querySelectorAll('.player-filter').forEach(el => { el.hidden = isGame; });
    setDefaultSort();
    showCard();
}

// sidebar on wide screens, slide-out panel ("Sort and Filter" button) on narrow screens, like the other pages
function alterImpactSidebar() {
    const panel = $('#offcanvasImpactFilters');
    if (document.body.clientWidth < 800) {
        panel.addClass('offcanvas offcanvas-start').removeClass('sidebar-buhs');
        $('#ocImpactHeader').removeClass('sidebar-header-center');
        panel.css('display', 'flex');
    } else {
        panel.removeClass('offcanvas offcanvas-start').addClass('sidebar-buhs');
        $('#ocImpactHeader').addClass('sidebar-header-center');
    }
}

function resetImpactCards() {
    icView.value = 'game';
    const seasons = unique(IC_GAMES.map(g => g.season)).sort();
    icGameSeason.value = seasons[seasons.length - 1];          // current season
    updateGameList();
    icPlayer.value = '';
    updatePlayerSeasons();
    showView();
}

function initImpactCards() {
    // seasons listed oldest first; the page opens on the current season
    const seasons = unique(IC_GAMES.map(g => g.season)).sort();
    fillSelect(icGameSeason, [{ value: 'all', text: 'All Seasons' }].concat(seasons.map(s => ({ value: s, text: s }))), seasons[seasons.length - 1]);
    updateGameList();

    const players = unique(IC_ROWS.map(r => r[1])).sort((a, b) => {
        const la = a.split(' ').slice(-1)[0], lb = b.split(' ').slice(-1)[0];       // by last name
        return la === lb ? a.localeCompare(b) : la.localeCompare(lb);
    });
    fillSelect(icPlayer, [{ value: '', text: 'Select a player' }].concat(players.map(p => ({ value: p, text: p }))));
    updatePlayerSeasons();

    icView.addEventListener('change', showView);
    icGameSeason.addEventListener('change', function () { updateGameList(icGame.value); showCard(); });
    icGame.addEventListener('change', showCard);
    icPlayer.addEventListener('change', function () { updatePlayerSeasons(); showCard(); });
    icPlayerSeason.addEventListener('change', showCard);
    icShowEx.addEventListener('change', function () {
        updateGameList(icGame.value);
        updatePlayerSeasons();
        showCard();
    });
    icSort.addEventListener('change', function () {
        // Date and Name go oldest / A first; every stat goes highest first
        icAscending.value = (icSort.value === 'date' || icSort.value === 'name') ? 'true' : 'false';
        showArrows();
        showCard();
    });
    document.getElementById('icResetButton').addEventListener('click', resetImpactCards);
    document.getElementById('icSaveButton').addEventListener('click', saveCardPNG);
    embeddedFontFace();      // fetch the font for saved images ahead of time, so the Save button responds right away
    alterImpactSidebar();
    document.addEventListener('scroll', hideTip, { passive: true });

    // phones fire 'resize' while scrolling (the address bar shows / hides), so only redraw
    // when the width really changes
    let resizeTimer;
    let lastWidth = window.innerWidth;
    window.addEventListener('resize', function () {
        if (window.innerWidth === lastWidth) return;
        lastWidth = window.innerWidth;
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(function () { alterImpactSidebar(); drawCard(icCurrentRows); }, 150);
    });
    showView();
}

// jQuery and Bootstrap load at the bottom of the layout, so start once the page has loaded
document.addEventListener('DOMContentLoaded', initImpactCards);
