const ticketId = document.getElementById("ticketId");
const ticketTitle = document.getElementById("ticketTitle");
const ticketDescription = document.getElementById("ticketDescription");

const generateBtn = document.getElementById("generateBtn");
const copyBtn = document.getElementById("copyBtn");
const exportBtn = document.getElementById("exportBtn");

const characterCount = document.getElementById("characterCount");

const emptyState = document.getElementById("emptyState");
const loadingState = document.getElementById("loadingState");
const result = document.getElementById("result");
const resultSubtitle = document.getElementById("resultSubtitle");
const loadingText = document.getElementById("loadingText");

let generatedText = "";

ticketDescription.addEventListener("input", () => {
    const count = ticketDescription.value.length;

    characterCount.textContent =
        `${count.toLocaleString()} character${count === 1 ? "" : "s"}`;
});

generateBtn.addEventListener("click", async () => {

    const id = ticketId.value.trim();
    const title = ticketTitle.value.trim();
    const description = ticketDescription.value.trim();

    if (!title && !description) {
        showError("Please provide a Jira summary or description.");
        return;
    }

    emptyState.classList.add("hidden");
    result.classList.add("hidden");
    loadingState.classList.remove("hidden");

    generateBtn.disabled = true;

    const messages = [
        "Reading Jira requirement...",
        "Identifying acceptance criteria...",
        "Building test scenarios...",
        "Checking positive and negative coverage..."
    ];

    let messageIndex = 0;

    loadingText.textContent = messages[messageIndex];

    const loadingInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % messages.length;
        loadingText.textContent = messages[messageIndex];
    }, 1200);

    try {

        /*
         * This endpoint will connect to your FastAPI backend.
         * We will build the backend next.
         */

        const response = await fetch("/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                ticket_id: id,
                title: title,
                description: description,
                coverage: document.getElementById("coverage").value,
                test_types: document.getElementById("testTypes").value
            })
        });

        if (!response.ok) {
            throw new Error("Unable to generate test cases.");
        }

        const data = await response.json();

        generatedText = data.result || "";

        renderResults(generatedText);

    } catch (error) {

        showError(
            "The test case generator could not connect to the backend. " +
            "Make sure the FastAPI server is running."
        );

    } finally {

        clearInterval(loadingInterval);

        loadingState.classList.add("hidden");
        generateBtn.disabled = false;
    }
});


function renderResults(text) {

    result.innerHTML = `
        <div class="result-summary">
            <div class="summary-card">
                <div class="summary-number">AI</div>
                <div class="summary-label">Generated</div>
            </div>

            <div class="summary-card">
                <div class="summary-number">QA</div>
                <div class="summary-label">Manual Test Cases</div>
            </div>
        </div>

        <div class="test-case">
            <div class="test-case-header">
                <div>
                    <div class="test-case-id">
                        GENERATED OUTPUT
                    </div>

                    <div class="test-case-title">
                        AI-generated QA test cases
                    </div>
                </div>

                <span class="test-type positive">
                    READY
                </span>
            </div>

            <div class="test-case-body">
                <div class="test-section">
                    <div class="test-section-title">
                        Test Cases
                    </div>

                    <div class="test-section-content">
                        ${formatText(text)}
                    </div>
                </div>
            </div>
        </div>
    `;

    result.classList.remove("hidden");

    resultSubtitle.textContent =
        "Generated from the provided Jira requirement.";

    copyBtn.disabled = false;
    exportBtn.disabled = false;
}


function formatText(text) {

    return escapeHtml(text)
        .replace(/\n\n/g, "<br><br>")
        .replace(/\n/g, "<br>");
}


function escapeHtml(text) {

    const div = document.createElement("div");
    div.textContent = text;

    return div.innerHTML;
}


function showError(message) {

    emptyState.classList.add("hidden");
    loadingState.classList.add("hidden");

    result.innerHTML = `
        <div class="test-case">
            <div class="test-case-body">
                <div class="test-section">
                    <div class="test-section-title">
                        Error
                    </div>

                    <div class="test-section-content">
                        ${escapeHtml(message)}
                    </div>
                </div>
            </div>
        </div>
    `;

    result.classList.remove("hidden");
}


copyBtn.addEventListener("click", async () => {

    if (!generatedText) {
        return;
    }

    await navigator.clipboard.writeText(generatedText);

    const originalText = copyBtn.textContent;

    copyBtn.textContent = "Copied";

    setTimeout(() => {
        copyBtn.textContent = originalText;
    }, 1500);
});


exportBtn.addEventListener("click", () => {

    if (!generatedText) {
        return;
    }

    const blob = new Blob(
        [generatedText],
        { type: "text/plain;charset=utf-8" }
    );

    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");

    link.href = url;
    link.download = "qa-test-cases.txt";

    link.click();

    URL.revokeObjectURL(url);
});