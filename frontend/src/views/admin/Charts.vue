<template>
  <div>
    <nav class="navbar navbar-dark bg-dark px-4">
      <span class="navbar-brand fw-bold">Placement Portal - Admin</span>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-light btn-sm" @click="$router.push('/admin/dashboard')">Dashboard</button>
        <button class="btn btn-outline-light btn-sm" @click="handleLogout">Logout</button>
      </div>
    </nav>

    <div class="container-fluid mt-4 px-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h4 class="mb-0">Analytics and Reports</h4>
        <button class="btn btn-sm btn-outline-secondary" @click="clearCache">
          Clear Cache
        </button>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
        <p class="mt-2 text-muted">Loading analytics...</p>
      </div>

      <div v-if="error" class="alert alert-danger">{{ error }}</div>

      <div v-if="!loading && data">
        <div class="row g-4 mb-4">
          <div class="col-lg-6">
            <div class="card shadow-sm h-100">
              <div class="card-body">
                <h6 class="card-title">Application Funnel</h6>
                <canvas ref="funnelChart" height="200"></canvas>
              </div>
            </div>
          </div>
          <div class="col-lg-6">
            <div class="card shadow-sm h-100">
              <div class="card-body">
                <h6 class="card-title">Monthly Trends</h6>
                <canvas ref="trendsChart" height="200"></canvas>
              </div>
            </div>
          </div>
        </div>

        <div class="row g-4 mb-4">
          <div class="col-lg-6">
            <div class="card shadow-sm h-100">
              <div class="card-body">
                <h6 class="card-title">Top Skills in Demand</h6>
                <div v-if="!data.top_skills || data.top_skills.length === 0"
                     class="text-center text-muted py-4">
                  No skills data yet. Add skills to placement drives.
                </div>
                <canvas v-else ref="skillsChart" height="200"></canvas>
              </div>
            </div>
          </div>
          <div class="col-lg-6">
            <div class="card shadow-sm h-100">
              <div class="card-body">
                <h6 class="card-title">Company Performance</h6>
                <div class="table-responsive mt-2">
                  <table class="table table-sm table-hover">
                    <thead class="table-dark">
                      <tr>
                        <th>Company</th>
                        <th>Drives</th>
                        <th>Applicants</th>
                        <th>Selected</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="c in data.company_stats" :key="c.name">
                        <td>{{ c.name }}</td>
                        <td>{{ c.drives }}</td>
                        <td>{{ c.applications }}</td>
                        <td><span class="badge bg-success">{{ c.selected }}</span></td>
                      </tr>
                      <tr v-if="!data.company_stats || data.company_stats.length === 0">
                        <td colspan="4" class="text-center text-muted">No data yet</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)
import analyticsService from '@/services/analyticsService'
import api from '@/services/api'

export default {
  name: 'AdminCharts',
  data() {
    return {
      loading: true,
      data: null,
      error: '',
      charts: {}
    }
  },
  async mounted() {
    await this.loadData()
  },
  beforeUnmount() {
    Object.values(this.charts).forEach(function(c) { if (c) c.destroy() })
  },
  methods: {
     async loadData() {
  this.loading = true
  this.error = ''
  try {
    this.data = await analyticsService.getAdminOverview()
    this.loading = false  // ✅ set false FIRST so canvas renders in DOM
    await this.$nextTick()  // ✅ wait for DOM to update
    this.renderAllCharts()  // ✅ now refs exist
  } catch (err) {
    console.log('Analytics load error', err)
    this.error = 'Failed to load analytics. Make sure Flask is running.'
    this.loading = false
  }
},

    renderAllCharts() {
      this.renderFunnel()
      this.renderTrends()
      this.renderSkills()
    },

    renderFunnel() {
      const ctx = this.$refs.funnelChart
      if (!ctx || !this.data.application_funnel) return
      if (this.charts.funnel) this.charts.funnel.destroy()
      this.charts.funnel = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: this.data.application_funnel.map(f => f.stage),
          datasets: [{
            label: 'Students',
            data: this.data.application_funnel.map(f => f.count),
            backgroundColor: [
              '#0d6efd','#0dcaf0','#ffc107','#198754','#6f42c1'
            ]
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
        }
      })
    },

    renderTrends() {
      const ctx = this.$refs.trendsChart
      if (!ctx || !this.data.monthly_trends) return
      if (this.charts.trends) this.charts.trends.destroy()
      this.charts.trends = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.data.monthly_trends.map(m => m.month),
          datasets: [
            {
              label: 'Applications',
              data: this.data.monthly_trends.map(m => m.applications),
              borderColor: '#0d6efd',
              backgroundColor: 'rgba(13,110,253,0.1)',
              tension: 0.4,
              fill: true
            },
            {
              label: 'Selected',
              data: this.data.monthly_trends.map(m => m.selected),
              borderColor: '#198754',
              tension: 0.4,
              fill: false
            },
            {
              label: 'Drives',
              data: this.data.monthly_trends.map(m => m.drives),
              borderColor: '#ffc107',
              tension: 0.4,
              fill: false
            }
          ]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'top' } },
          scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } }
        }
      })
    },

    renderSkills() {
      const ctx = this.$refs.skillsChart
      if (!ctx || !this.data.top_skills || this.data.top_skills.length === 0) return
      if (this.charts.skills) this.charts.skills.destroy()
      this.charts.skills = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: this.data.top_skills.map(s => s.skill),
          datasets: [{
            data: this.data.top_skills.map(s => s.count),
            backgroundColor: [
              '#0d6efd','#6610f2','#6f42c1','#d63384',
              '#dc3545','#fd7e14','#ffc107','#198754',
              '#20c997','#0dcaf0'
            ]
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'right' } }
        }
      })
    },

    async clearCache() {
      try {
        await api.post('/api/analytics/cache/clear')
        await this.loadData()
      } catch (err) {
        console.log('Cache clear error', err)
      }
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