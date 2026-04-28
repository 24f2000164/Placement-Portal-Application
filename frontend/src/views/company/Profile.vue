<template>
  <div>
    <nav class="navbar navbar-dark bg-success px-4">
      <span class="navbar-brand fw-bold">Placement Portal</span>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-light btn-sm" @click="$router.push('/company/dashboard')">
          Back to Dashboard
        </button>
        <button class="btn btn-outline-light btn-sm" @click="handleLogout">Logout</button>
      </div>
    </nav>

    <div class="container mt-4" style="max-width: 700px;">
      <h4 class="mb-4">Company Profile</h4>

      <div v-if="message" class="alert alert-success">{{ message }}</div>
      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div class="card">
        <div class="card-header">
          <strong>Company Information</strong>
        </div>
        <div class="card-body">
          <div class="mb-3">
            <label class="form-label">Company Name</label>
            <input v-model="form.company_name" type="text" class="form-control" />
          </div>
          <div class="row">
            <div class="col mb-3">
              <label class="form-label">Industry</label>
              <input v-model="form.industry" type="text" class="form-control" placeholder="e.g. IT, Finance" />
            </div>
            <div class="col mb-3">
              <label class="form-label">Location</label>
              <input v-model="form.location" type="text" class="form-control" placeholder="City, Country" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Website</label>
            <input v-model="form.website" type="url" class="form-control" placeholder="https://company.com" />
          </div>
          <div class="row">
            <div class="col mb-3">
              <label class="form-label">HR Contact Name</label>
              <input v-model="form.hr_contact" type="text" class="form-control" />
            </div>
            <div class="col mb-3">
              <label class="form-label">HR Phone</label>
              <input v-model="form.hr_phone" type="text" class="form-control" />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Company Description</label>
            <textarea v-model="form.description" class="form-control" rows="4" placeholder="Tell students about your company"></textarea>
          </div>
          <button class="btn btn-success" @click="saveProfile" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save Profile' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import companyService from '@/services/companyService'

export default {
  name: 'CompanyProfile',
  data() {
    return {
      form: {
        company_name: '',
        industry: '',
        location: '',
        website: '',
        hr_contact: '',
        hr_phone: '',
        description: ''
      },
      saving: false,
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
        const data = await companyService.getProfile()
        this.form.company_name = data.company_name || ''
        this.form.industry = data.industry || ''
        this.form.location = data.location || ''
        this.form.website = data.website || ''
        this.form.hr_contact = data.hr_contact || ''
        this.form.hr_phone = data.hr_phone || ''
        this.form.description = data.description || ''
      } catch (err) {
        this.error = 'Failed to load profile'
      }
    },

    async saveProfile() {
      this.saving = true
      this.message = ''
      this.error = ''
      try {
        await companyService.updateProfile(this.form)
        this.message = 'Profile saved successfully'
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to save profile'
      } finally {
        this.saving = false
      }
    },

    handleLogout() {
      this.logout()
      this.$router.push('/login')
    }
  }
}
</script>