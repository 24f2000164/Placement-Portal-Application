<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-4">
      <span class="navbar-brand fw-bold fs-4">Placement Portal</span>
      <div class="ms-auto d-flex gap-2">
        <router-link to="/login" class="btn btn-outline-light btn-sm">Login</router-link>
        <router-link to="/register" class="btn btn-primary btn-sm">Register</router-link>
      </div>
    </nav>

    <div class="bg-dark text-white py-5 text-center">
      <div class="container">
        <h1 class="display-5 fw-bold mb-3">Campus Placement Portal</h1>
        <p class="lead text-secondary mb-4">Connecting students with top companies for placement drives</p>
        <router-link to="/register" class="btn btn-primary btn-lg me-2">Get Started</router-link>
        <router-link to="/login" class="btn btn-outline-light btn-lg">Sign In</router-link>
      </div>
    </div>

    <div class="bg-light py-5">
      <div class="container">
        <h2 class="text-center mb-4">Placement Statistics</h2>
        <div class="row g-3 justify-content-center" v-if="stats">
          <div class="col-md-2 col-6">
            <div class="card text-center border-0 shadow-sm">
              <div class="card-body py-4">
                <h2 class="text-primary fw-bold">{{ stats.total_companies }}</h2>
                <p class="small text-muted mb-0">Companies</p>
              </div>
            </div>
          </div>
          <div class="col-md-2 col-6">
            <div class="card text-center border-0 shadow-sm">
              <div class="card-body py-4">
                <h2 class="text-success fw-bold">{{ stats.total_drives }}</h2>
                <p class="small text-muted mb-0">Active Drives</p>
              </div>
            </div>
          </div>
          <div class="col-md-2 col-6">
            <div class="card text-center border-0 shadow-sm">
              <div class="card-body py-4">
                <h2 class="text-info fw-bold">{{ stats.total_students }}</h2>
                <p class="small text-muted mb-0">Students</p>
              </div>
            </div>
          </div>
          <div class="col-md-2 col-6">
            <div class="card text-center border-0 shadow-sm">
              <div class="card-body py-4">
                <h2 class="text-warning fw-bold">{{ stats.total_selected }}</h2>
                <p class="small text-muted mb-0">Selections</p>
              </div>
            </div>
          </div>
          <div class="col-md-2 col-6">
            <div class="card text-center border-0 shadow-sm">
              <div class="card-body py-4">
                <h2 class="text-danger fw-bold">{{ stats.total_placed }}</h2>
                <p class="small text-muted mb-0">Placed</p>
              </div>
            </div>
          </div>
        </div>

        <div class="row mt-5" v-if="trends.length > 0">
          <div class="col-12">
            <div class="card border-0 shadow-sm">
              <div class="card-body">
                <h5 class="card-title mb-4">Monthly Placement Trends</h5>
                <canvas ref="landingChart" height="100"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="py-5">
      <div class="container">
        <h2 class="text-center mb-5">How It Works</h2>
        <div class="row g-4 text-center">
          <div class="col-md-4">
            <div class="p-4">
              <div class="display-4 mb-3">📝</div>
              <h5>Register</h5>
              <p class="text-muted">Students and companies register on the portal with their details</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="p-4">
              <div class="display-4 mb-3">🏢</div>
              <h5>Companies Post Drives</h5>
              <p class="text-muted">Approved companies create placement drives with eligibility criteria</p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="p-4">
              <div class="display-4 mb-3">🎓</div>
              <h5>Students Apply</h5>
              <p class="text-muted">Eligible students apply and track their application status in real time</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="bg-dark text-white text-center py-3">
      <p class="mb-0 small">Placement Portal - Institute Placement Cell System</p>
    </div>
  </div>
</template>

<script>

import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)
import analyticsService from '@/services/analyticsService'

export default {
  name: 'Landing',
  data() {
    return {
      stats: null,
      trends: [],
      chart: null
    }
  },
  async mounted() {
    await this.loadData()
  },
  beforeUnmount() {
    if (this.chart) this.chart.destroy()
  },
  methods: {
    async loadData() {
      try {
        this.stats  = await analyticsService.getPublicStats()
        this.trends = await analyticsService.getPublicTrends()
        if (this.trends.length > 0) {
          await this.$nextTick()
          this.renderChart()
        }
      } catch (err) {
        console.log('Landing data load error', err)
      }
    },

    renderChart() {
      const ctx = this.$refs.landingChart   
      if (!ctx) return
      if (this.chart) this.chart.destroy()
      this.chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.trends.map(t => t.month),
          datasets: [
            {
              label: 'Applications',
              data: this.trends.map(t => t.applications),
              borderColor: '#0d6efd',
              backgroundColor: 'rgba(13,110,253,0.1)',
              fill: true,
              tension: 0.4
            },
            {
              label: 'Selected',
              data: this.trends.map(t => t.selected),
              borderColor: '#198754',
              backgroundColor: 'rgba(25,135,84,0.1)',
              fill: true,
              tension: 0.4
            }
          ]
        },
        options: {
          responsive: true,
          plugins: { legend: { position: 'top' } },
          scales: { y: { beginAtZero: true } }
        }
      })
    }
  }
}
</script>