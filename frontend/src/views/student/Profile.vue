<template>
  <div>
    <nav class="navbar navbar-dark bg-primary px-4">
      <span class="navbar-brand fw-bold">Placement Portal</span>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-light btn-sm" @click="$router.push('/student/dashboard')">
          Back to Dashboard
        </button>
        <button class="btn btn-outline-light btn-sm" @click="handleLogout">Logout</button>
      </div>
    </nav>

    <div class="container mt-4" style="max-width: 700px;">
      <h4 class="mb-4">My Profile</h4>

      <div v-if="message" class="alert alert-success">{{ message }}</div>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div class="card mb-4">
        <div class="card-header">
          <strong>Personal Information</strong>
        </div>
        <div class="card-body">
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input v-model="form.full_name" type="text" class="form-control" placeholder="Your full name" />
          </div>
          <div class="mb-3">
            <label class="form-label">Phone</label>
            <input v-model="form.phone" type="text" class="form-control" placeholder="Phone number" />
          </div>
          <div class="row">
            <div class="col mb-3">
              <label class="form-label">Branch</label>
              <input v-model="form.branch" type="text" class="form-control" placeholder="e.g. CSE, ECE" />
            </div>
            <div class="col mb-3">
              <label class="form-label">CGPA</label>
              <input v-model="form.cgpa" type="number" step="0.01" min="0" max="10" class="form-control" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Year</label>
            <select v-model="form.year" class="form-select">
              <option value="1">1st Year</option>
              <option value="2">2nd Year</option>
              <option value="3">3rd Year</option>
              <option value="4">4th Year</option>
            </select>
          </div>
          <div class="mb-3">
            <label class="form-label">Skills</label>
            <input v-model="form.skills" type="text" class="form-control" placeholder="e.g. Python, Java, SQL" />
            <div class="form-text">Comma separated skills</div>
          </div>
          <div class="mb-3">
            <label class="form-label">Experience</label>
            <input v-model="form.experience" type="text" class="form-control"
              placeholder="e.g. Fresher, 6 months internship at XYZ" />
          </div>
          <div class="mb-3">
            <label class="form-label"> Linkdin Url</label>
            <input v-model="form.linkdin_url" type="text" class="form-control" placeholder="Please provide your Linkdin Profile URL" />

          </div>
          <button class="btn btn-primary" @click="saveProfile" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save Profile' }}
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <strong>Resume Upload</strong>
        </div>
        <div class="card-body">
          <div v-if="currentResume" class="alert alert-info mb-3">
            Current resume: {{ currentResume }}
          </div>
          <div class="mb-3">
            <label class="form-label">Upload Resume</label>
            <input
              type="file"
              class="form-control"
              accept=".pdf,.doc,.docx"
              @change="onFileChange"
            />
            <div class="form-text">Accepted formats: PDF, DOC, DOCX. Max 5MB.</div>
          </div>
          <button class="btn btn-success" @click="uploadResume" :disabled="!resumeFile || uploading">
            {{ uploading ? 'Uploading...' : 'Upload Resume' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import studentService from '@/services/studentService'

export default {
  name: 'StudentProfile',
  data() {
    return {
      form: {
        full_name: '',
        phone: '',
        branch: '',
        cgpa: '',
        year: 1,
        skills: '',
        experience: ''
      },
      resumeFile: null,
      currentResume: '',
      saving: false,
      uploading: false,
      message: '',
      error: ''
    }
  },
  async mounted() {
    await this.loadProfile()
  },
  methods: {
    ...mapActions('auth', ['logout']),

    async loadProfile() {
      try {
        const data = await studentService.getProfile()
        this.form.full_name = data.full_name || ''
        this.form.phone = data.phone || ''
        this.form.branch = data.branch || ''
        this.form.cgpa = data.cgpa || ''
        this.form.year = data.year || 1
        this.form.skills = data.skills || ''
        this.form.experience  = data.experience || ''
        this.currentResume = data.resume_path || ''
      } catch (err) {
        this.error = 'Failed to load profile'
      }
    },

    async saveProfile() {
      this.saving = true
      this.message = ''
      this.error = ''
      try {
        await studentService.updateProfile(this.form)
        this.message = 'Profile saved successfully'
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to save profile'
      } finally {
        this.saving = false
      }
    },

    onFileChange(event) {
      this.resumeFile = event.target.files[0]
    },

    async uploadResume() {
      if (!this.resumeFile) return
      this.uploading = true
      this.message = ''
      this.error = ''
      try {
        await studentService.uploadResume(this.resumeFile)
        this.message = 'Resume uploaded successfully'
        await this.loadProfile()
      } catch (err) {
       
         if (err.response?.status === 413) {
      this.error = 'File is too large. Please upload a file under 10MB.'
    } else {
      this.error = err.response?.data?.message || 'Failed to upload resume'
    }
      } finally {
        this.uploading = false
      }
    },

    handleLogout() {
      this.logout()
      this.$router.push('/login')
    }
  }
}
</script>