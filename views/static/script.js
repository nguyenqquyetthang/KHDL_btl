const submitBtn = document.getElementById("submitBtn");
const queryInput = document.getElementById("query");
const topKInput = document.getElementById("top_k");
const errorBox = document.getElementById("error");
const resultsBox = document.getElementById("results");

const chartRefs = {
    rating: null,
    genre: null,
    topItems: null,
};

async function fetchJson(url, options = {}) {
    const res = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    if (!res.ok) {
        const payload = await res.json().catch(() => ({}));
        throw new Error(payload.error || "Có lỗi xảy ra");
    }
    return res.json();
}

function renderResults(items) {
    resultsBox.innerHTML = "";
    if (!items.length) {
        resultsBox.innerHTML = "<p>Không tìm thấy gợi ý phù hợp.</p>";
        return;
    }

    items.forEach((item) => {
        const div = document.createElement("div");
        div.className = "result-item";
        const overview = item.overview || "Không có mô tả";
        const overviewPreview = overview.length > 150 ? overview.substring(0, 150) + "..." : overview;
        const releaseYear = item.release_date ? new Date(item.release_date).getFullYear() : item.year;
        div.innerHTML = `
            <div class="result-title">${item.title}</div>
            <div class="result-meta">${item.genres} • Rating: ${item.rating.toFixed(1)}/10${releaseYear ? " • " + releaseYear : ""}</div>
            <div class="result-overview">${overviewPreview}</div>
            <div class="result-score">Độ tương đồng: ${(item.score * 100).toFixed(2)}%</div>
        `;
        // Thêm sự kiện click để lưu vào lịch sử xem
        div.addEventListener("click", () => {
            saveViewHistory(item.id, item.title, item.genres, item.rating);
        });
        resultsBox.appendChild(div);
    });
}

async function handleRecommend() {
    errorBox.textContent = "";
    resultsBox.innerHTML = "";

    const query = queryInput.value.trim();
    const top_k = Number(topKInput.value) || 10;

    if (!query) {
        errorBox.textContent = "Vui lòng nhập từ khóa.";
        return;
    }

    try {
        submitBtn.disabled = true;
        submitBtn.textContent = "Đang gợi ý...";
        const data = await fetchJson("/api/recommend", {
            method: "POST",
            body: JSON.stringify({ query, top_k }),
        });
        renderResults(data.results || []);
    } catch (err) {
        errorBox.textContent = err.message;
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Gợi ý ngay";
    }
}

function renderChart(chartName, ctx, type, data, options) {
    if (chartRefs[chartName]) {
        chartRefs[chartName].destroy();
    }
    chartRefs[chartName] = new Chart(ctx, {
        type,
        data,
        options,
    });
}

function renderHeatmap(heatmap) {
    const container = document.getElementById("heatmapGrid");
    if (!container) return;

    const labels = heatmap?.labels || [];
    const matrix = heatmap?.matrix || [];
    if (!labels.length || !matrix.length) {
        container.innerHTML = "<p>Không có dữ liệu heatmap.</p>";
        return;
    }

    const n = labels.length;
    const flat = matrix.flat();
    const max = Math.max(...flat);
    const min = Math.min(...flat);
    const grid = document.createElement("div");
    grid.className = "heatmap-table";
    grid.style.gridTemplateColumns = `repeat(${n + 1}, minmax(60px, 1fr))`;

    const addHeader = (text) => {
        const h = document.createElement("div");
        h.className = "heatmap-header";
        h.textContent = text;
        return h;
    };

    grid.appendChild(addHeader(""));
    labels.forEach((l) => grid.appendChild(addHeader(l)));

    for (let i = 0; i < n; i++) {
        grid.appendChild(addHeader(labels[i]));
        for (let j = 0; j < n; j++) {
            const val = matrix[i][j] ?? 0;
            const norm = max === min ? 0 : (val - min) / (max - min);
            const lightness = 90 - norm * 50;
            const cell = document.createElement("div");
            cell.className = "heatmap-cell";
            cell.style.backgroundColor = `hsl(190, 70%, ${lightness}%)`;
            cell.title = `${labels[i]} ↔ ${labels[j]}: ${(val * 100).toFixed(1)}%`;
            cell.textContent = `${(val * 100).toFixed(0)}%`;
            grid.appendChild(cell);
        }
    }

    container.innerHTML = "";
    container.appendChild(grid);
}

async function loadStats() {
    try {
        const stats = await fetchJson("/api/stats");

        renderChart(
            "rating",
            document.getElementById("ratingChart"),
            "bar",
            {
                labels: stats.rating_distribution.bins.slice(0, -1).map((b, i) => `${b.toFixed(1)} - ${stats.rating_distribution.bins[i + 1].toFixed(1)}`),
                datasets: [
                    {
                        label: "Số phim",
                        data: stats.rating_distribution.counts,
                        backgroundColor: "rgba(34, 211, 238, 0.6)",
                        borderColor: "rgba(34, 211, 238, 0.9)",
                        borderWidth: 1,
                        barPercentage: 1,
                        categoryPercentage: 1,
                    },
                ],
            },
            {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y}`,
                        },
                    },
                },
                scales: { y: { beginAtZero: true } },
            }
        );

        renderChart(
            "genre",
            document.getElementById("genreChart"),
            "bar",
            {
                labels: stats.genre_counts.labels,
                datasets: [
                    {
                        label: "Tần suất",
                        data: stats.genre_counts.counts,
                        backgroundColor: "rgba(94, 234, 212, 0.7)",
                    },
                ],
            },
            {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: "y",
                // Dùng mode "point" + intersect để tooltip bám đúng thanh đang hover
                interaction: { mode: "point", intersect: true, axis: "y" },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.x}`,
                        },
                    },
                },
                scales: { x: { beginAtZero: true } },
            }
        );

        renderChart(
            "topItems",
            document.getElementById("topItemsChart"),
            "bar",
            {
                labels: stats.top_items.titles,
                datasets: [
                    {
                        label: "Rating",
                        data: stats.top_items.ratings,
                        backgroundColor: "rgba(251, 191, 36, 0.7)",
                    },
                ],
            },
            {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}`,
                        },
                    },
                },
                scales: { y: { beginAtZero: true, max: 10 } },
            }
        );

        renderHeatmap(stats.heatmap);
    } catch (err) {
        console.error(err);
    }
}

// Lưu lịch sử xem phim
async function saveViewHistory(movieId, title, genres, rating) {
    try {
        await fetchJson("/api/history/view", {
            method: "POST",
            body: JSON.stringify({
                movie_id: movieId,
                title: title,
                genres: genres,
                rating: rating,
            }),
        });
        loadHistory(); // Cập nhật UI
    } catch (err) {
        console.error("Lỗi lưu lịch sử:", err);
    }
}

// Load lịch sử
async function loadHistory() {
    try {
        const history = await fetchJson("/api/history");
        renderSearchHistory(history.searches || []);
        renderViewHistory(history.views || []);
    } catch (err) {
        console.error("Lỗi load lịch sử:", err);
    }
}

function renderSearchHistory(searches) {
    const container = document.getElementById("searchHistory");
    if (!searches.length) {
        container.innerHTML = "<p class='empty-msg'>Chưa có lịch sử tìm kiếm</p>";
        return;
    }
    container.innerHTML = searches
        .map((s) => {
            const date = new Date(s.timestamp).toLocaleString("vi-VN");
            return `
                <div class="history-item">
                    <div class="history-query">"${s.query}"</div>
                    <div class="history-meta">${s.result_count} kết quả • ${date}</div>
                </div>
            `;
        })
        .join("");
}

function renderViewHistory(views) {
    const container = document.getElementById("viewHistory");
    if (!views.length) {
        container.innerHTML = "<p class='empty-msg'>Chưa có phim đã xem</p>";
        return;
    }
    container.innerHTML = views
        .map((v) => {
            const date = new Date(v.timestamp).toLocaleString("vi-VN");
            return `
                <div class="history-item">
                    <div class="history-title">${v.title}</div>
                    <div class="history-meta">${v.genres} • Rating: ${v.rating.toFixed(1)}/10 • ${date}</div>
                </div>
            `;
        })
        .join("");
}

// Clear lịch sử
async function clearHistory() {
    if (!confirm("Bạn có chắc muốn xóa toàn bộ lịch sử?")) return;
    try {
        await fetchJson("/api/history/clear", { method: "POST" });
        loadHistory();
    } catch (err) {
        console.error("Lỗi xóa lịch sử:", err);
    }
}

// Tab switching
function initHistoryTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    tabBtns.forEach((btn) => {
        btn.addEventListener("click", () => {
            const targetTab = btn.dataset.tab;
            tabBtns.forEach((b) => b.classList.remove("active"));
            tabContents.forEach((c) => c.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById(`${targetTab}-tab`).classList.add("active");
        });
    });

    document.getElementById("clearHistoryBtn").addEventListener("click", clearHistory);
}


submitBtn.addEventListener("click", handleRecommend);
window.addEventListener("load", () => {
    loadStats();
    loadHistory();
    initHistoryTabs();
});
