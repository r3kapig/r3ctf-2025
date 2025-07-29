class PigSayEncryptTool {
    constructor() {
        this.initializeElements()
        this.bindEvents()
        this.selectedFile = null
        this.currentResultData = null

        window.app = this
    }

    initializeElements() {
        // Text elements
        this.textInput = document.getElementById("textInput")
        this.textOutput = document.getElementById("textOutput")
        this.encryptBtn = document.getElementById("encryptBtn")
        this.decryptBtn = document.getElementById("decryptBtn")
        this.clearTextBtn = document.getElementById("clearTextBtn")
        this.copyBtn = document.getElementById("copyBtn")

        // File elements
        this.fileUploadArea = document.getElementById("fileUploadArea")
        this.fileInput = document.getElementById("fileInput")
        this.fileInfo = document.getElementById("fileInfo")
        this.fileName = document.getElementById("fileName")
        this.fileSize = document.getElementById("fileSize")
        this.removeFileBtn = document.getElementById("removeFileBtn")
        this.encryptFileBtn = document.getElementById("encryptFileBtn")
        this.decryptFileBtn = document.getElementById("decryptFileBtn")
        this.fileResult = document.getElementById("fileResult")
        this.resultContent = document.getElementById("resultContent")
        this.downloadBtn = document.getElementById("downloadBtn")

        // UI elements
        this.loadingOverlay = document.getElementById("loadingOverlay")
        this.toastContainer = document.getElementById("toastContainer")
    }

    bindEvents() {
        // Text encryption events
        this.encryptBtn.addEventListener("click", () => this.handleTextEncrypt())
        this.decryptBtn.addEventListener("click", () => this.handleTextDecrypt())
        this.clearTextBtn.addEventListener("click", () => this.clearText())
        this.copyBtn.addEventListener("click", () => this.copyResult())

        // File upload events
        this.fileUploadArea.addEventListener("click", () => this.fileInput.click())
        this.fileUploadArea.addEventListener("dragover", (e) => this.handleDragOver(e))
        this.fileUploadArea.addEventListener("dragleave", (e) => this.handleDragLeave(e))
        this.fileUploadArea.addEventListener("drop", (e) => this.handleDrop(e))
        this.fileInput.addEventListener("change", (e) => this.handleFileSelect(e))
        this.removeFileBtn.addEventListener("click", () => this.removeFile())

        // File encryption events
        this.encryptFileBtn.addEventListener("click", () => this.handleFileEncrypt())
        this.decryptFileBtn.addEventListener("click", () => this.handleFileDecrypt())
    }

    // Text encryption methods
    async handleTextEncrypt() {
        const text = this.textInput.value.trim()
        if (!text) {
            this.showToast("Please enter text to encrypt", "error")
            return
        }

        this.showLoading()
        try {
            const response = await fetch("/api/encrypt", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ text: text }),
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const result = await response.json()
            if (result.code !== 20000) {
                throw new Error(result.msg || "Encryption failed")
            }

            this.textOutput.value = result.data || result.result || "Encryption completed"
            this.showToast("Text encrypted successfully!", "success")
        } catch (error) {
            console.error("Encryption error:", error)
            this.showToast("Encryption failed: " + error.message, "error")
        } finally {
            this.hideLoading()
        }
    }

    async handleTextDecrypt() {
        const text = this.textInput.value.trim()
        if (!text) {
            this.showToast("Please enter text to decrypt", "error")
            return
        }

        this.showLoading()
        try {
            const response = await fetch("/api/decrypt", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ text: text }),
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const result = await response.json()
            if (result.code !== 20000) {
                throw new Error(result.msg || "Decryption failed")
            }

            this.textOutput.value = result.data || result.result || "Decryption completed"
            this.showToast("Text decrypted successfully!", "success")
        } catch (error) {
            console.error("Decryption error:", error)
            this.showToast("Decryption failed: " + error.message, "error")
        } finally {
            this.hideLoading()
        }
    }

    clearText() {
        this.textInput.value = ""
        this.textOutput.value = ""
        this.showToast("Text cleared", "info")
    }

    async copyResult() {
        const text = this.textOutput.value
        if (!text) {
            this.showToast("No result to copy", "error")
            return
        }

        try {
            await navigator.clipboard.writeText(text)
            this.showToast("Result copied to clipboard!", "success")
        } catch (error) {
            // Fallback for older browsers
            this.textOutput.select()
            document.execCommand("copy")
            this.showToast("Result copied to clipboard!", "success")
        }
    }

    // File handling methods
    handleDragOver(e) {
        e.preventDefault()
        this.fileUploadArea.classList.add("dragover")
    }

    handleDragLeave(e) {
        e.preventDefault()
        this.fileUploadArea.classList.remove("dragover")
    }

    handleDrop(e) {
        e.preventDefault()
        this.fileUploadArea.classList.remove("dragover")
        const files = e.dataTransfer.files
        if (files.length > 0) {
            this.processFile(files[0])
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0]
        if (file) {
            this.processFile(file)
        }
    }

    processFile(file) {
        const allowedTypes = [".zip", ".rar", ".tar.gz", ".7z"]
        const fileName = file.name.toLowerCase()
        const isValidType = allowedTypes.some((type) => fileName.endsWith(type))

        if (!isValidType) {
            this.showToast("Invalid file type. Please upload .zip, .rar, .tar.gz, or .7z files.", "error")
            return
        }

        this.selectedFile = file
        this.displayFileInfo(file)
        this.enableFileButtons()
    }

    displayFileInfo(file) {
        this.fileName.textContent = file.name
        this.fileSize.textContent = this.formatFileSize(file.size)
        this.fileInfo.style.display = "flex"
        this.fileUploadArea.style.display = "none"
    }

    removeFile() {
        this.selectedFile = null
        this.fileInfo.style.display = "none"
        this.fileUploadArea.style.display = "block"
        this.fileInput.value = ""
        this.disableFileButtons()
        this.hideFileResult()
    }

    enableFileButtons() {
        this.encryptFileBtn.disabled = false
        this.decryptFileBtn.disabled = false
    }

    disableFileButtons() {
        this.encryptFileBtn.disabled = true
        this.decryptFileBtn.disabled = true
    }

    async handleFileEncrypt() {
        if (!this.selectedFile) {
            this.showToast("Please select a file first", "error")
            return
        }

        this.showLoading()
        try {
            const formData = new FormData()
            formData.append("file", this.selectedFile)

            const response = await fetch("/api/file/encrypt", {
                method: "POST",
                body: formData,
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const result = await response.json()

            if (result.code !== 20000) {
                throw new Error(result.msg || "Encryption failed")
            }

            this.displayFileResult(result.data, "Encryption", result.msg)
            this.showToast("File encrypted successfully!", "success")
        } catch (error) {
            console.error("File encryption error:", error)
            this.showToast("File encryption failed: " + error.message, "error")
        } finally {
            this.hideLoading()
        }
    }

    async handleFileDecrypt() {
        if (!this.selectedFile) {
            this.showToast("Please select a file first", "error")
            return
        }

        this.showLoading()
        try {
            const formData = new FormData()
            formData.append("file", this.selectedFile)

            const response = await fetch("/api/file/decrypt", {
                method: "POST",
                body: formData,
            })

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`)
            }

            const result = await response.json()

            if (result.code !== 20000) {
                throw new Error(result.msg || "Decryption failed")
            }

            this.displayFileResult(result.data, "Decryption", result.msg)
            this.showToast("File decrypted successfully!", "success")
        } catch (error) {
            console.error("File decryption error:", error)
            this.showToast("File decryption failed: " + error.message, "error")
        } finally {
            this.hideLoading()
        }
    }

    displayFileResult(data, operation, message) {
        const fileCount = Object.keys(data).length

        let resultHtml = `
      <div class="result-header">
        <strong>${operation} completed successfully!</strong>
        <div class="result-stats">
          <span>Files processed: ${fileCount}</span>
          <span>Status: ${message}</span>
        </div>
      </div>
      <div class="files-container">
    `

        Object.entries(data).forEach(([filename, content]) => {
            const truncatedContent = content.length > 200 ? content.substring(0, 200) + "..." : content
            resultHtml += `
        <div class="file-item">
          <div class="file-header">
            <span class="file-icon">📄</span>
            <span class="file-title">${filename}</span>
            <div class="file-actions">
              <button class="btn btn-small" onclick="app.copyFileContent('${filename}', \`${content.replace(/`/g, "\\`")}\`)">
                <span class="btn-icon">📋</span>
                Copy
              </button>
              <button class="btn btn-small" onclick="app.downloadFileContent('${filename}', \`${content.replace(/`/g, "\\`")}\`)">
                <span class="btn-icon">⬇️</span>
                Download
              </button>
            </div>
          </div>
          <div class="file-content">
            <pre>${truncatedContent}</pre>
            ${content.length > 200 ? `<button class="btn btn-small show-more-btn" onclick="app.toggleFileContent(this, \`${content.replace(/`/g, "\\`")}\`)">Show More</button>` : ""}
          </div>
        </div>
      `
        })

        resultHtml += `
      </div>
      <div class="result-actions">
        <button class="btn btn-success" onclick="app.downloadAllFiles()">
          <span class="btn-icon">📦</span>
          Download All Files
        </button>
      </div>
    `

        this.resultContent.innerHTML = resultHtml
        this.fileResult.style.display = "block"

        this.currentResultData = data
    }

    hideFileResult() {
        this.fileResult.style.display = "none"
    }

    downloadResult(url) {
        const link = document.createElement("a")
        link.href = url
        link.download = ""
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        this.showToast("Download started!", "success")
    }

    copyFileContent(filename, content) {
        try {

            navigator.clipboard
                .writeText(content)
                .then(() => {
                    this.showToast(`Content of ${filename} copied to clipboard!`, "success")
                })
        } catch {
            const textArea = document.createElement("textarea")
            textArea.value = content
            document.body.appendChild(textArea)
            textArea.select()
            document.execCommand("copy")
            document.body.removeChild(textArea)
            this.showToast(`Content of ${filename} copied to clipboard!`, "success")
        }

    }

    downloadFileContent(filename, content) {
        const blob = new Blob([content], { type: "text/plain" })
        const url = URL.createObjectURL(blob)
        const link = document.createElement("a")
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        this.showToast(`${filename} downloaded!`, "success")
    }

    toggleFileContent(button, fullContent) {
        const fileContent = button.parentElement.querySelector("pre")
        const isExpanded = button.textContent === "Show Less"

        if (isExpanded) {
            fileContent.textContent = fullContent.substring(0, 200) + "..."
            button.textContent = "Show More"
        } else {
            fileContent.textContent = fullContent
            button.textContent = "Show Less"
        }
    }

    downloadAllFiles() {
        if (!this.currentResultData) {
            this.showToast("No files to download", "error")
            return
        }

        let allContent = "=== PigSay Encryption/Decryption Results ===\n\n"

        Object.entries(this.currentResultData).forEach(([filename, content]) => {
            allContent += `=== ${filename} ===\n${content}\n\n`
        })

        const blob = new Blob([allContent], { type: "text/plain" })
        const url = URL.createObjectURL(blob)
        const link = document.createElement("a")
        link.href = url
        link.download = "pigsay_results.txt"
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        this.showToast("All files downloaded as pigsay_results.txt!", "success")
    }

    // Utility methods
    formatFileSize(bytes) {
        if (bytes === 0) return "0 Bytes"
        const k = 1024
        const sizes = ["Bytes", "KB", "MB", "GB"]
        const i = Math.floor(Math.log(bytes) / Math.log(k))
        return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
    }

    showLoading() {
        // this.loadingOverlay.style.display = "flex"
    }

    hideLoading() {
        // this.loadingOverlay.style.display = "none"
    }

    showToast(message, type = "info") {
        const toast = document.createElement("div")
        toast.className = `toast ${type}`

        const icon = type === "success" ? "✅" : type === "error" ? "❌" : "ℹ️"
        toast.innerHTML = `
            <span style="font-size: 18px;">${icon}</span>
            <span>${message}</span>
        `

        this.toastContainer.appendChild(toast)

        // Auto remove after 4 seconds
        setTimeout(() => {
            toast.style.animation = "slideOut 0.3s ease forwards"
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast)
                }
            }, 300)
        }, 4000)
    }
}

// Initialize the application when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    new PigSayEncryptTool()
})

// Add some interactive effects
document.addEventListener("DOMContentLoaded", () => {
    // Add floating animation to cards
    const cards = document.querySelectorAll(".card")
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.2}s`
        card.classList.add("fade-in")
    })

    // Add ripple effect to buttons
    const buttons = document.querySelectorAll(".btn")
    buttons.forEach((button) => {
        button.addEventListener("click", function (e) {
            const ripple = document.createElement("span")
            const rect = this.getBoundingClientRect()
            const size = Math.max(rect.width, rect.height)
            const x = e.clientX - rect.left - size / 2
            const y = e.clientY - rect.top - size / 2

            ripple.style.width = ripple.style.height = size + "px"
            ripple.style.left = x + "px"
            ripple.style.top = y + "px"
            ripple.classList.add("ripple")

            this.appendChild(ripple)

            setTimeout(() => {
                ripple.remove()
            }, 600)
        })
    })
})

// Add CSS for animations
const style = document.createElement("style")
style.textContent = `
    .fade-in {
        opacity: 0;
        transform: translateY(30px);
        animation: fadeInUp 0.6s ease forwards;
    }

    @keyframes fadeInUp {
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: rippleEffect 0.6s linear;
        pointer-events: none;
    }

    @keyframes rippleEffect {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }

    .btn {
        position: relative;
        overflow: hidden;
    }
`
document.head.appendChild(style)
