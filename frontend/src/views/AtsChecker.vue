<template>
  <div>
    <nav class="navbar navbar-dark bg-secondary px-4">
      <span class="navbar-brand fw-bold">ATS Resume Screener</span>
      <button class="btn btn-outline-light btn-sm" @click="$router.go(-1)">Back</button>
    </nav>

    <div class="container mt-4" style="max-width: 900px;">
      <div class="card shadow-sm mb-4">
        <div class="card-body">
          <h5 class="card-title">ATS Style Resume Checker</h5>
          <p class="text-muted small">
            Paste your resume text and the job description below.
            The ATS checker will score your resume against the job requirements.
          </p>

          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label fw-bold">Job Description</label>
              <textarea
                v-model="jobDescription"
                class="form-control"
                rows="10"
                placeholder="Paste the job description here..."
              ></textarea>
            </div>
            <div class="col-md-6"><div class="mb-3">
  <label class="form-label fw-bold">Upload Resume (PDF / TXT)</label>
  <input 
    type="file" 
    class="form-control" 
    @change="handleFileUpload"
    accept=".txt,.pdf,.doc,.docx"
  />
</div>

              <label class="form-label fw-bold">Your Resume Text</label>
              
              <textarea
                v-model="resumeText"
                class="form-control"
                rows="10"
                placeholder="Paste your resume content here..."
              ></textarea>
            </div>          </div>

          <button
            class="btn btn-primary mt-3"
            @click="analyzeResume"
            :disabled="!jobDescription || !resumeText || analyzing"
          >
            {{ analyzing ? 'Analyzing...' : 'Analyze Resume' }}
          </button>
        </div>
      </div>

      <div v-if="result" class="card shadow-sm">
        <div class="card-body">
          <h5 class="card-title">ATS Analysis Result</h5>

          <div class="row g-3 mb-4">
            <div class="col-md-4 text-center">
              <div class="p-3 rounded" :class="scoreClass">
                <h1 class="display-4 fw-bold">{{ result.score }}%</h1>
                <p class="mb-0 fw-bold">ATS Score</p>
              </div>
            </div>
            <div class="col-md-8">
              <div class="mb-3">
                <label class="form-label fw-bold">Score Breakdown</label>
                <div class="progress mb-2" style="height: 20px;">
                  <div
                    class="progress-bar"
                    :class="progressClass"
                    :style="{ width: result.score + '%' }"
                  >{{ result.score }}%</div>
                </div>
              </div>
              <p class="mb-1">
                <strong>Verdict:</strong>
                <span class="badge ms-2" :class="verdictBadge">{{ result.verdict }}</span>
              </p>
              <p class="mb-0 text-muted small">{{ result.summary }}</p>
            </div>
          </div>

          <div class="row g-3">
            <div class="col-md-6">
              <div class="card border-success">
                <div class="card-header bg-success text-white py-2">
                  <strong>Matched Keywords ({{ result.matched_keywords.length }})</strong>
                </div>
                <div class="card-body py-2">
                  <div v-if="result.matched_keywords.length > 0" class="d-flex flex-wrap gap-1">
                    <span
                      v-for="kw in result.matched_keywords"
                      :key="kw"
                      class="badge bg-success"
                    >{{ kw }}</span>
                  </div>
                  <p v-else class="text-muted small mb-0">No keywords matched</p>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="card border-danger">
                <div class="card-header bg-danger text-white py-2">
                  <strong>Missing Keywords ({{ result.missing_keywords.length }})</strong>
                </div>
                <div class="card-body py-2">
                  <div v-if="result.missing_keywords.length > 0" class="d-flex flex-wrap gap-1">
                    <span
                      v-for="kw in result.missing_keywords"
                      :key="kw"
                      class="badge bg-danger"
                    >{{ kw }}</span>
                  </div>
                  <p v-else class="text-muted small mb-0">No missing keywords</p>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-4">
            <h6>Improvement Suggestions</h6>
            <ul class="list-group">
              <li
                v-for="(tip, index) in result.suggestions"
                :key="index"
                class="list-group-item list-group-item-warning"
              >
                {{ tip }}
              </li>
              <li v-if="result.suggestions.length === 0" class="list-group-item list-group-item-success">
                Great job! Your resume is well aligned with the job description.
              </li>
            </ul>
          </div>

          <div class="mt-4">
            <h6>Section Check</h6>
            <div class="row g-2">
              <div
                v-for="section in result.sections"
                :key="section.name"
                class="col-md-3 col-6"
              >
                <div
                  class="card text-center py-2"
                  :class="section.found ? 'border-success' : 'border-danger'"
                >
                  <div class="card-body py-1">
                    <span class="fs-4">{{ section.found ? 'yes' : 'no' }}</span>
                    <p class="small mb-0 mt-1" :class="section.found ? 'text-success' : 'text-danger'">
                      {{ section.name }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <button class="btn btn-outline-secondary mt-4" @click="reset">
            Check Another Resume
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AtsChecker',
  data() {
    return {
      jobDescription: '',
      resumeText: '',
      analyzing: false,
      result: null
    }
  },
  computed: {
    scoreClass() {
      if (!this.result) return ''
      if (this.result.score >= 75) return 'bg-success text-white rounded'
      if (this.result.score >= 50) return 'bg-warning text-dark rounded'
      return 'bg-danger text-white rounded'
    },
    progressClass() {
      if (!this.result) return 'bg-secondary'
      if (this.result.score >= 75) return 'bg-success'
      if (this.result.score >= 50) return 'bg-warning'
      return 'bg-danger'
    },
    verdictBadge() {
      if (!this.result) return 'bg-secondary'
      if (this.result.score >= 75) return 'bg-success'
      if (this.result.score >= 50) return 'bg-warning text-dark'
      return 'bg-danger'
    }
  },
  methods: {
    analyzeResume() {
      this.analyzing = true
      this.result = null

      setTimeout(() => {
        this.result = this.runAtsAnalysis(this.jobDescription, this.resumeText)
        this.analyzing = false
      }, 1200)
    },

    runAtsAnalysis(jd, resume) {
      const jdLower     = jd.toLowerCase()
      const resumeLower = resume.toLowerCase()

      const stopWords = new Set([
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'shall', 'can', 'not', 'this', 'that', 'these',
        'those', 'it', 'its', 'we', 'our', 'you', 'your', 'they', 'their',
        'as', 'if', 'so', 'than', 'then', 'also', 'into', 'about', 'which'
      ])

      const extractKeywords = function(text) {
        const words = text.match(/\b[a-zA-Z][a-zA-Z0-9+#.]{1,}\b/g) || []
        const freq = {}
        words.forEach(function(w) {
          const lower = w.toLowerCase()
          if (!stopWords.has(lower) && lower.length > 2) {
            freq[lower] = (freq[lower] || 0) + 1
          }
        })
        return Object.keys(freq).filter(function(k) { return freq[k] >= 1 })
      }

      const techKeywords = [
        'python', 'java', 'javascript', 'react', 'vue', 'angular', 'node',
        'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'flask', 'django',
        'spring', 'docker', 'kubernetes', 'aws', 'azure', 'git', 'linux',
        'machine learning', 'deep learning', 'data analysis', 'tensorflow',
        'pandas', 'numpy', 'html', 'css', 'rest', 'api', 'agile', 'scrum',
        'typescript', 'kotlin', 'swift', 'golang', 'rust', 'c++', 'c#'
      ]

      const jdKeywords = extractKeywords(jdLower)
      const importantJdKeywords = jdKeywords.filter(function(k) {
        return techKeywords.includes(k) || jdLower.split(k).length > 2
      })

      const finalJdKeywords = importantJdKeywords.length > 5
        ? importantJdKeywords
        : jdKeywords.slice(0, 20)

      const matched = finalJdKeywords.filter(function(k) {
        return resumeLower.includes(k)
      })

      const missing = finalJdKeywords.filter(function(k) {
        return !resumeLower.includes(k)
      })

      const keywordScore = finalJdKeywords.length > 0
        ? Math.round((matched.length / finalJdKeywords.length) * 100)
        : 0

      const sections = [
        { name: 'Education',    keywords: ['education', 'degree', 'bachelor', 'master', 'b.tech', 'b.e', 'university', 'college'] },
        { name: 'Experience',   keywords: ['experience', 'internship', 'worked', 'project', 'developed', 'built'] },
        { name: 'Skills',       keywords: ['skills', 'technologies', 'tools', 'proficient', 'expertise'] },
        { name: 'Contact Info', keywords: ['email', 'phone', 'linkedin', 'github', 'contact'] }
      ]

      const sectionResults = sections.map(function(s) {
        const found = s.keywords.some(function(k) { return resumeLower.includes(k) })
        return { name: s.name, found: found }
      })

      const sectionScore   = Math.round((sectionResults.filter(function(s) { return s.found }).length / sections.length) * 100)
      const lengthScore    = resume.split(' ').length >= 150 ? 100 : Math.round((resume.split(' ').length / 150) * 100)
      const finalScore     = Math.round((keywordScore * 0.6) + (sectionScore * 0.25) + (lengthScore * 0.15))
      const clampedScore   = Math.min(100, Math.max(0, finalScore))

      let verdict = 'Poor Match'
      let summary = 'Your resume needs significant improvement to pass ATS screening for this role.'
      if (clampedScore >= 75) {
        verdict = 'Strong Match'
        summary = 'Your resume is well aligned with the job description and likely to pass ATS screening.'
      } else if (clampedScore >= 50) {
        verdict = 'Moderate Match'
        summary = 'Your resume partially matches the job requirements. Add missing keywords to improve your score.'
      }

      const suggestions = []
      if (missing.length > 0) {
        suggestions.push('Add these missing keywords naturally in your resume: ' + missing.slice(0, 5).join(', '))
      }
      if (!sectionResults.find(function(s) { return s.name === 'Skills' }).found) {
        suggestions.push('Add a dedicated Skills section listing your technical skills')
      }
      if (!sectionResults.find(function(s) { return s.name === 'Experience' }).found) {
        suggestions.push('Add an Experience or Projects section with concrete achievements')
      }
      if (resume.split(' ').length < 150) {
        suggestions.push('Your resume seems short. Add more details about your experience and projects')
      }
      if (resume.split(' ').length > 700) {
        suggestions.push('Your resume is very long. Try to keep it under 2 pages for ATS optimization')
      }

      return {
        score:            clampedScore,
        verdict:          verdict,
        summary:          summary,
        matched_keywords: matched.slice(0, 20),
        missing_keywords: missing.slice(0, 20),
        sections:         sectionResults,
        suggestions:      suggestions
      }
    },

    handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return

      // Plain text file — read directly
      if (file.type === 'text/plain' || file.name.endsWith('.txt')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          this.resumeText = e.target.result
        }
        reader.readAsText(file)
        return
      }

      // PDF — extract text via pdf.js (loaded from CDN in index.html)
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
        const reader = new FileReader()
        reader.onload = async (e) => {
          try {
            const pdfjsLib = window['pdfjs-dist/build/pdf']
            if (!pdfjsLib) {
              this.resumeText = '[PDF parsing not available — please paste your resume text manually]'
              return
            }
            pdfjsLib.GlobalWorkerOptions.workerSrc =
              'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js'
            const typedArray = new Uint8Array(e.target.result)
            const pdf = await pdfjsLib.getDocument({ data: typedArray }).promise
            let fullText = ''
            for (let i = 1; i <= pdf.numPages; i++) {
              const page = await pdf.getPage(i)
              const content = await page.getTextContent()
              fullText += content.items.map(item => item.str).join(' ') + '\n'
            }
            this.resumeText = fullText.trim()
          } catch (err) {
            this.resumeText = '[Could not parse PDF — please paste your resume text manually]'
          }
        }
        reader.readAsArrayBuffer(file)
        return
      }

      // DOC/DOCX or anything else — tell user to paste
      this.resumeText = '[This file type cannot be read in the browser — please paste your resume text manually]'
    },

    reset() {
      this.result         = null
      this.jobDescription = ''
      this.resumeText     = ''
      // also clear the file input visually
      const fileInput = this.$el.querySelector('input[type="file"]')
      if (fileInput) fileInput.value = ''
    }
  }
}
</script>