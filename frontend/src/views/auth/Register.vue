<template>
  <div class="container-fluid min-vh-100 d-flex align-items-center justify-content-center bg-light">
    <div class="card shadow" style="width: 480px;">
      <div class="card-body p-4">
        <h4 class="card-title text-center mb-2">Create Account</h4>
        <h6 class="text-center text-muted mb-4">Register as Student or Company</h6>

        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>

        <div class="mb-3">
          <label class="form-label">Register as</label>
          <select v-model="role" class="form-select">
            <option value="student">Student</option>
            <option value="company">Company</option>
          </select>
        </div>

        <form @submit.prevent="handleRegister">
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="form.email" type="email" class="form-control" placeholder="Enter email" required />
          </div>

          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password" class="form-control" placeholder="Min 6 characters" required />
          </div>

          <div v-if="role === 'student'">
            <div class="mb-3">
              <label class="form-label">Full Name</label>
              <input v-model="form.full_name" type="text" class="form-control" placeholder="Enter full name" required />
            </div>
            <div class="row">
              <div class="col mb-3">
                <label class="form-label">Branch</label>
                <input v-model="form.branch" type="text" class="form-control" placeholder="e.g. CSE" />
              </div>
              <div class="col mb-3">
                <label class="form-label">CGPA</label>
                <input v-model="form.cgpa" type="number" step="0.01" min="0" max="10" class="form-control" placeholder="e.g. 8.5" />
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
              <label class="form-label">Phone</label>
              <input v-model="form.phone" type="text" class="form-control" placeholder="Phone number" />
            </div>
          </div>

          <div v-if="role === 'company'">
            <div class="mb-3">
              <label class="form-label">Company Name</label>
              <input v-model="form.company_name" type="text" class="form-control" placeholder="Enter company name" required />
            </div>
            <div class="mb-3">
              <label class="form-label">Industry</label>
              <input v-model="form.industry" type="text" class="form-control" placeholder="e.g. IT, Finance" />
            </div>
            <div class="mb-3">
              <label class="form-label">HR Contact Name</label>
              <input v-model="form.hr_contact" type="text" class="form-control" placeholder="HR person name" />
            </div>
            <div class="mb-3">
              <label class="form-label">Website</label>
              <input v-model="form.website" type="url" class="form-control" placeholder="https://company.com" />
            </div>
            <div class="mb-3">
              <label class="form-label">Location</label>
              <input v-model="form.location" type="text" class="form-control" placeholder="City, Country" />
            </div>
          </div>

          <button type="submit" class="btn btn-success w-100" :disabled="loading">
            <span v-if="loading">Registering...</span>
            <span v-else>Register</span>
          </button>
        </form>

        <hr />
        <p class="text-center mb-0">
          Already have an account?
          <router-link to="/login">Login here</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Register',
  data() {
    return {
      role: 'student',
      form: {
        email: '',
        password: '',
        full_name: '',
        branch: '',
        cgpa: '',
        year: 1,
        phone: '',
        company_name: '',
        industry: '',
        hr_contact: '',
        website: '',
        location: ''
      },
      loading: false,
      error: '',
      success: ''
    }
  },
  methods: {
    ...mapActions('auth', ['registerStudent', 'registerCompany']),
    async handleRegister() {
      this.loading = true
      this.error = ''
      this.success = ''
      try {
        if (this.role === 'student') {
          await this.registerStudent(this.form)
          this.success = 'Student registered successfully. Please login.'
        } else {
          await this.registerCompany(this.form)
          this.success = 'Company registered. Awaiting admin approval before login.'
        }
        setTimeout(() => {
          this.$router.push('/login')
        }, 2000)
      } catch (err) {
        this.error = err.response?.data?.message || 'Registration failed.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>