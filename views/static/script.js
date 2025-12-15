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
                    },
                ],
            },
            {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
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
                plugins: { legend: { display: false } },
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
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, max: 10 } },
            }
        );
    } catch (err) {
        console.error(err);
    }
}

submitBtn.addEventListener("click", handleRecommend);
window.addEventListener("load", loadStats);
