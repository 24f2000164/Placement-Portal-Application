<template>
  <div>
    <nav class="navbar navbar-dark bg-primary px-4">
      <span class="navbar-brand fw-bold">Placement Portal</span>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-light btn-sm" @click="$router.push('/student/dashboard')">Dashboard</button>
        <button class="btn btn-outline-light btn-sm" @click="handleLogout">Logout</button>
      </div>
    </nav>

    <div class="container-fluid mt-4 px-4">
      <h4 class="mb-4">My Applications</h4>

      <div v-if="applications.length === 0" class="text-center py-5 text-muted">
        You have not applied to any drives yet.
      </div>

      <div v-for="app in applications" :key="app.id" class="card mb-3 shadow-sm">
        <div class="card-body">
          <div class="row align-items-center">
            <div class="col-md-4">
              <h6 class="mb-1">{{ app.drive_title }}</h6>
              <p class="text-muted small mb-1">{{ app.company_name }}</p>
              <p class="small mb-0">Applied: {{ formatDate(app.applied_at) }}</p>
            </div>

            <div class="col-md-4">
              <div class="d-flex align-items-center gap-2 mb-2">
                <span class="badge" :class="statusBadge(app.status)">{{ app.status }}</span>
              </div>

              <div class="d-flex gap-1 flex-wrap">
                <span
                  v-for="s in allStatuses"
                  :key="s"
                  class="badge"
                  :class="getStatusStepClass(s, app.status)"
                  style="font-size: 10px;"
                >{{ s }}</span>
              </div>
            </div>

            <div class="col-md-4">
              <div v-if="app.interview">
                <p class="small mb-1"><strong>Interview:</strong> {{ app.interview.mode }}</p>
                <p class="small mb-1"><strong>Date:</strong> {{ formatDate(app.interview.scheduled_at) }}</p>
                <p class="small mb-1"><strong>Venue:</strong> {{ app.interview.venue || 'N/A' }}</p>
                <p class="small mb-0"><strong>Result:</strong>
                  <span class="badge" :class="resultBadge(app.interview.result)">
                    {{ app.interview.result }}
                  </span>
                </p>
              </div>
              <p v-else class="text-muted small">No interview scheduled yet</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import studentService from '@/services/studentService'

export default {
  name: 'StudentApplications',
  data() {
    return {
      applications: [],
      allStatuses: ['applied', 'shortlisted', 'interview', 'offer', 'selected', 'placed']
    }
  },
  async mounted() {
    await this.loadApplications()
  },
  methods: {
    async loadApplications() {
      try {
        this.applications = await studentService.getMyApplications()
      } catch (err) {
        console.log(err)
      }
    },

    getStatusStepClass(step, currentStatus) {
      const order = ['applied', 'shortlisted', 'interview', 'offer', 'selected', 'placed']
      const currentIndex = order.indexOf(currentStatus)
      const stepIndex = order.indexOf(step)

      if (currentStatus === 'rejected') {
        return stepIndex === 0 ? 'bg-danger' : 'bg-light text-dark'
      }

      if (stepIndex < currentIndex) return 'bg-success'
      if (stepIndex === currentIndex) return 'bg-primary'
      return 'bg-light text-dark border'
    },

    statusBadge(status) {
      if (status === 'selected') return 'bg-success'
      if (status === 'shortlisted') return 'bg-info text-dark'
      if (status === 'applied') return 'bg-primary'
      if (status === 'rejected') return 'bg-danger'
      if (status === 'interview') return 'bg-warning text-dark'
      if (status === 'placed') return 'bg-success'
      if (status === 'offer') return 'bg-info'
      return 'bg-secondary'
    },

    resultBadge(result) {
      if (result === 'passed') return 'bg-success'
      if (result === 'failed') return 'bg-danger'
      return 'bg-warning text-dark'
    },

    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleDateString('en-IN')
    },

    handleLogout() {
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      localStorage.removeItem('user')
      this.$store.commit('auth/CLEAR_AUTH')
      this.$router.push('/login')
    }
  }
}
</script>