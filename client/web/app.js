const API = "http://localhost:5000";
const FACTS = API + "/api/facts";
const TODAY = API + "/api/facts/today";
const RANDOM = API + "/api/facts/random";
const FAV = API + "/api/favorites";
const STATS = API + "/api/stats";

// Troca abas
function openTab(name) {
    document.querySelectorAll(".tab").forEach(t => t.style.display = "none");
    document.getElementById(name).style.display = "block";

    if (name === "admin") loadFacts();
    if (name === "facts") getToday();
    if (name === "fav") loadFavorites();
    if (name === "stats") loadStats();
}

// FACTS ADMIN
function loadFacts() {
    fetch(FACTS + "?format=json")
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("facts_list");
            container.textContent = ""; // limpa conteúdo

            if (!data.facts || data.facts.length === 0) {
                container.textContent = "Nenhum fact encontrado.";
                return;
            }

            data.facts.forEach(f => {
                container.textContent +=
`ID: ${f.id}
Texto: ${f.text || "N/A"}
Fonte: ${f.source || "N/A"}
Idioma: ${f.language || "N/A"}
Salvo em: ${f.saved_at || "N/A"}
--------------------------------------------------\n`;
            });
        });
}

async function createFact() {
    const payload = {
        text: document.getElementById("text").value,
        source: document.getElementById("source").value,
        language: document.getElementById("lang").value,
    };

    await fetch(FACTS, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    });

    alert("Fact criado!");
    loadFacts();
}

async function deleteFact() {
    const id = document.getElementById("delete_id").value;
    await fetch(`${FACTS}/${id}`, {method: "DELETE"});
    alert("Fact deletado!");
    loadFacts();
}

// USER FACTS
function getToday() {
    fetch(TODAY + "?format=json")
        .then(res => res.json())
        .then(data => {
            const fact = data.fact;
            const container = document.getElementById("today");
            container.textContent = ""; // limpa conteúdo
            container.textContent +=
`ID: ${fact.id}
Texto: ${fact.text || "N/A"}
Fonte: ${fact.source || "N/A"}
Idioma: ${fact.language || "N/A"}
Link: ${fact.permalink || "N/A"}`;
            window.todayFact = fact;
        });
}

function getRandom() {
    fetch(RANDOM + "?format=json")
        .then(res => res.json())
        .then(data => {
            const fact = data.fact;
            const container = document.getElementById("random");
            container.textContent = ""; // limpa conteúdo
            container.textContent +=
`ID: ${fact.id}
Texto: ${fact.text || "N/A"}
Fonte: ${fact.source || "N/A"}
Idioma: ${fact.language || "N/A"}
Link: ${fact.permalink || "N/A"}`;
            window.randomFact = fact;
        });
}

async function favoriteToday() {
    const note = prompt("Nota (opcional):");
    await fetch(FAV, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            fact_text: JSON.stringify(window.todayFact),
            notes: note
        })
    });
    alert("Favorito salvo!");
}

async function favoriteRandom() {
    const note = prompt("Nota:");
    await fetch(FAV, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            fact_text: JSON.stringify(window.randomFact),
            notes: note
        })
    });
    alert("Favorito salvo!");
}

async function loadFavorites() {
    const res = await fetch(FAV + "?format=json");
    const data = await res.json();
    const favList = document.getElementById("fav_list");
    favList.textContent = ""; // limpa conteúdo

    if (!data.favorites || data.favorites.length === 0) {
        favList.textContent = "Nenhum favorito encontrado.";
        return;
    }

    data.favorites.forEach(f => {
        let fact = {};
        try {
            const parsed = JSON.parse(f.fact_text);
            fact = parsed.fact || parsed || {};
        } catch(e) {
            fact = { text: f.fact_text };
        }

        favList.textContent +=
`ID: ${f.id}
Texto: ${fact.text || "N/A"}
Fonte: ${fact.source || "N/A"}
Idioma: ${fact.language || "N/A"}
Nota: ${f.notes || ""}
Adicionado em: ${f.added_at}
--------------------------------------------------\n`;
    });
}


async function removeFavorite() {
    const id = document.getElementById("fav_id").value;
    await fetch(`${FAV}/${id}`, {method: "DELETE"});
    alert("Favorito removido!");
    loadFavorites();
}

// ESTATÍSTICAS
function loadStats() {
    fetch(STATS + "?format=json")
        .then(res => res.json())
        .then(data => {
            const stats = data.statistics;
            const container = document.getElementById("stats_box");
            container.textContent = ""; // limpa conteúdo
            container.textContent +=
`Total de Facts: ${stats.total_facts || 0}
Total de Favoritos: ${stats.total_favorites || 0}

Facts por Fonte:
${Object.entries(stats.facts_by_source || {}).map(([k,v]) => `- ${k}: ${v}`).join("\n")}

Facts por Idioma:
${Object.entries(stats.facts_by_language || {}).map(([k,v]) => `- ${k}: ${v}`).join("\n")}

Gerado em: ${stats.generated_at || "N/A"}`;
        });
}

// Inicializa
openTab("admin");