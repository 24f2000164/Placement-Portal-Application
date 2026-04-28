<template>
  <div>
    <nav class="navbar navbar-dark bg-primary px-4">
      <span class="navbar-brand fw-bold">Placement Portal</span>
      <div class="d-flex gap-2 align-items-center">
        <span class="text-white small">{{ studentName }}</span>
        <button class="btn btn-outline-light btn-sm" @click="goToProfile">Profile</button>
        <button class="btn btn-outline-light btn-sm" @click="handleLogout">Logout</button>


        <button class="btn btn-outline-light btn-sm" @click="$router.push('/ats')">ATS Checker</button>


      </div>
    </nav>

    <div class="container-fluid mt-4 px-4">

      <div class="row mb-3">
        <div class="col">
           <h4>Welcome, {{ studentName || 'Student' }} 👋</h4>
          <p class="text-muted">Browse and apply to placement drives</p>
        </div>
      </div>

      <ul class="nav nav-tabs mb-4">
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'drives' }" href="#" @click.prevent="tab = 'drives'">
            Available Drives
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'applications' }" href="#" @click.prevent="tab = 'applications'">
            My Applications
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'history' }" href="#" @click.prevent="tab = 'history'">
            Placement History
          </a>
        </li>
      </ul>

      <div v-if="message" class="alert alert-success alert-dismissible">
        {{ message }}
        <button type="button" class="btn-close" @click="message = ''"></button>
      </div>

      <div v-if="error" class="alert alert-danger alert-dismissible">
        {{ error }}
        <button type="button" class="btn-close" @click="error = ''"></button>
      </div>

      <div v-if="tab === 'drives'">
        <div class="row g-2 mb-3">
          <div class="col-md-5">
            <input
              v-model="searchQuery"
              type="text"
              class="form-control"
              placeholder="Search by job title, skills, location..."
              @input="loadDrives"
            />
          </div>
          <div class="col-md-3">
            <input
              v-model="branchFilter"
              type="text"
              class="form-control"
              placeholder="Filter by branch e.g. CSE"
              @input="loadDrives"
            />
          </div>
          <div class="col-md-2">
            <input
              v-model="cgpaFilter"
              type="number"
              step="0.1"
              min="0"
              max="10"
              class="form-control"
              placeholder="My CGPA"
              @input="loadDrives"
            />
          </div>
          <div class="col-md-2">
            <button class="btn btn-secondary w-100" @click="clearFilters">Clear</button>
          </div>
        </div>

        <div v-if="drives.length === 0" class="text-center py-5 text-muted">
          <p>No approved drives available right now.</p>
        </div>

        <div class="row g-3">
          <div class="col-md-6 col-lg-4" v-for="drive in drives" :key="drive.id">
            <div class="card h-100 shadow-sm">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <h6 class="card-title mb-0">{{ drive.job_title }}</h6>
                  <span class="badge bg-success">Open</span>
                </div>
                <p class="text-muted small mb-1">{{ drive.company_name }}</p>
                <p class="text-muted small mb-1">{{ drive.location }}</p>
                <hr />
                <div class="small mb-1">
                  <strong>Salary:</strong> {{ drive.salary || 'Not disclosed' }}
                </div>
                <div class="small mb-1">
                  <strong>Min CGPA:</strong> {{ drive.min_cgpa || 'No minimum' }}
                </div>
                <div class="small mb-1">
                  <strong>Branches:</strong> {{ drive.eligible_branches || 'All branches' }}
                </div>
                <div class="small mb-1">
                  <strong>Deadline:</strong> {{ formatDate(drive.application_deadline) }}
                </div>
                <div class="small mb-2">
                  <strong>Skills:</strong> {{ drive.skills_required || 'Not specified' }}
                </div>
                <p class="small text-muted mb-2">{{ truncate(drive.job_description) }}</p>
              </div>
              <div class="card-footer d-flex gap-2">
                <button
                  class="btn btn-primary btn-sm flex-grow-1"
                  @click="applyToDrive(drive.id)"
                  :disabled="alreadyApplied(drive.id)"
                >
                  {{ alreadyApplied(drive.id) ? 'Applied' : 'Apply Now' }}
                </button>
                <button
                  class="btn btn-outline-secondary btn-sm"
                  @click="viewDrive(drive)"
                >Details</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="tab === 'applications'">
  <h5 class="mb-3">My Applications</h5>

  <div v-if="applications.length === 0" class="text-center py-5 text-muted">
    <p>You have not applied to any drives yet.</p>
    <button class="btn btn-primary btn-sm" @click="tab = 'drives'">Browse Drives</button>
  </div>

  <div v-for="app in applications" :key="app.id" class="card mb-3 shadow-sm">
    <div class="card-header d-flex justify-content-between align-items-center">
      <div>
        <strong>{{ app.drive_title }}</strong>
        <span class="text-muted small ms-2">at {{ app.company_name }}</span>
      </div>
      <span class="badge" :class="statusBadge(app.status)">{{ app.status }}</span>
    </div>
    <div class="card-body">
      <div class="row">

        <div class="col-md-6">
          <h6 class="text-muted mb-3">Application Details</h6>
          <p class="small mb-1">
            <strong>Application ID:</strong> {{ app.id }}
          </p>
          <p class="small mb-1">
            <strong>Applied On:</strong> {{ formatDate(app.applied_at) }}
          </p>
          <p class="small mb-1">
            <strong>Last Updated:</strong> {{ formatDate(app.updated_at) }}
          </p>
          <p class="small mb-0">
            <strong>Current Status:</strong>
            <span class="badge ms-1" :class="statusBadge(app.status)">{{ app.status }}</span>
          </p>
        </div>

        <div class="col-md-6">
          <h6 class="text-muted mb-3">Interview Details</h6>
          <div v-if="app.interview">
            <p class="small mb-1">
              <strong>Mode:</strong>
              <span class="badge bg-info text-dark ms-1">{{ app.interview.mode }}</span>
            </p>
            <p class="small mb-1">
              <strong>Date and Time:</strong> {{ formatDate(app.interview.scheduled_at) }}
            </p>
            <p class="small mb-1" v-if="app.interview.venue">
              <strong>{{ app.interview.mode === 'Online' ? 'Meeting Link' : 'Venue' }}:</strong>
              
                <a v-if="app.interview.mode === 'Online'"
                :href="app.interview.venue"
                target="_blank"
                class="btn btn-sm btn-success ms-1"
              >Join Meeting</a>
              <span v-else class="ms-1">{{ app.interview.venue }}</span>
            </p>
            <p class="small mb-1" v-if="app.interview.notes">
              <strong>Notes:</strong> {{ app.interview.notes }}
            </p>
            <p class="small mb-0">
              <strong>Result:</strong>
              <span class="badge ms-1" :class="resultBadge(app.interview.result)">
                {{ app.interview.result }}
              </span>
            </p>
          </div>
          <p v-else class="text-muted small">No interview scheduled yet</p>
        </div>

      </div>

      <div class="mt-3">
        <h6 class="text-muted mb-2">Application Progress</h6>
        <div class="d-flex gap-1 flex-wrap">
          <span
            v-for="step in statusSteps"
            :key="step"
            class="badge"
            :class="getStepClass(step, app.status)"
            style="font-size: 11px; padding: 6px 10px;"
          >{{ step }}</span>
        </div>
      </div>


      <div v-if="app.feedback" class="alert alert-info py-1 px-2 mt-2 small">
  <strong>Company Feedback:</strong> {{ app.feedback }}
</div>
<button
  v-if="app.status === 'selected' || app.status === 'placed'"
  class="btn btn-success btn-sm mt-2"
  @click="downloadConfirmation(app.id)"
>
  ⬇ Download Confirmation
</button>




    </div>
  </div>
</div>

      <!-- <div v-if="tab === 'applications'">
        <h5 class="mb-3">My Applications</h5>
        <div class="table-responsive">
          <table class="table table-bordered table-hover">
            <thead class="table-dark">
              <tr>
                <th>ID</th>
                <th>Company</th>
                <th>Job Title</th>
                <th>Applied On</th>
                <th>Status</th>
                <th>Interview</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications" :key="app.id">
                <td>{{ app.id }}</td>
                <td>{{ app.company_name }}</td>
                <td>{{ app.drive_title }}</td>
                <td>{{ formatDate(app.applied_at) }}</td>
                <td>
                  <span class="badge" :class="statusBadge(app.status)">{{ app.status }}</span>
                </td>
              <td>
  <div v-if="app.interview">
    <p class="mb-1 small">
      <strong>Mode:</strong>
      <span class="badge bg-info text-dark">{{ app.interview.mode }}</span>
    </p>
    <p class="mb-1 small">
      <strong>Date:</strong> {{ formatDate(app.interview.scheduled_at) }}
    </p>
    <p class="mb-1 small" v-if="app.interview.venue">
      <strong>{{ app.interview.mode === 'Online' ? 'Meeting Link' : 'Venue' }}:</strong>
      
        <a v-if="app.interview.mode === 'Online'"
        :href="formatLink(app.interview.venue)"
        target="_blank"
        rel="noopener noreferrer"
        class="btn btn-sm btn-success ms-1"
        @click.stop
      >Join Meeting</a>
      <span v-else class="ms-1">{{ app.interview.venue }}</span>
    </p>
    <p class="mb-0 small" v-if="app.interview.notes">
      <strong>Notes:</strong> {{ app.interview.notes }}
    </p>
    <p class="mb-0 small">
      <strong>Result:</strong>
      <span class="badge ms-1" :class="resultBadge(app.interview.result)">
        {{ app.interview.result }}
      </span>
    </p>
  </div>
      <span v-else class="text-muted small">Not scheduled yet</span>
       </td>
                
                
              </tr>
              <tr v-if="applications.length === 0">
                <td colspan="6" class="text-center text-muted">You have not applied to any drives yet</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div> -->

      <div v-if="tab === 'history'">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5>Placement History</h5>
          <button class="btn btn-success btn-sm" @click="exportCSV">
            Export as CSV
          </button>
        </div>
        <div class="table-responsive">
          <table class="table table-bordered table-hover">
            <thead class="table-dark">
              <tr>
                <th>Drive No</th>
                <th>Company</th>
                <th>Job Title</th>
                <th>Applied On</th>
                <th>Interview Mode</th>
                <th>Interview Date</th>
                <th>Result</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(entry, index) in history" :key="entry.application_id">
                <td>{{ index + 1 }}</td>
                <td>{{ entry.company_name }}</td>
                <td>{{ entry.drive_title }}</td>
                <td>{{ formatDate(entry.applied_at) }}</td>
                <td>{{ entry.interview_mode || 'N/A' }}</td>
                <td>{{ formatDate(entry.interview_date) }}</td>
                <td>{{ entry.interview_result || 'N/A' }}</td>
                <td>
                  <span class="badge" :class="statusBadge(entry.status)">{{ entry.status }}</span>
                </td>
              </tr>
              <tr v-if="history.length === 0">
                <td colspan="8" class="text-center text-muted">No placement history yet</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <div v-if="selectedDrive" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedDrive.job_title }}</h5>
            <button type="button" class="btn-close" @click="selectedDrive = null"></button>
          </div>
          <div class="modal-body">
            <p><strong>Company:</strong> {{ selectedDrive.company_name }}</p>
            <p><strong>Location:</strong> {{ selectedDrive.location }}</p>
            <p><strong>Salary:</strong> {{ selectedDrive.salary || 'Not disclosed' }}</p>
            <p><strong>Min CGPA:</strong> {{ selectedDrive.min_cgpa || 'No minimum' }}</p>
            <p><strong>Eligible Branches:</strong> {{ selectedDrive.eligible_branches || 'All branches' }}</p>
            <p><strong>Eligible Year:</strong> {{ selectedDrive.eligible_year || 'All years' }}</p>
            <p><strong>Skills Required:</strong> {{ selectedDrive.skills_required || 'Not specified' }}</p>
            <p><strong>Application Deadline:</strong> {{ formatDate(selectedDrive.application_deadline) }}</p>
            <hr />
            <p><strong>Job Description:</strong></p>
            <p>{{ selectedDrive.job_description }}</p>
          </div>
          <div class="modal-footer">
            <button
              class="btn btn-primary"
              @click="applyToDrive(selectedDrive.id); selectedDrive = null"
              :disabled="alreadyApplied(selectedDrive.id)"
            >
              {{ alreadyApplied(selectedDrive.id) ? 'Already Applied' : 'Apply Now' }}
            </button>
            <button class="btn btn-secondary" @click="selectedDrive = null">Close</button>
          </div>
        </div>
      </div>
    </div>



  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import studentService from '@/services/studentService'

export default {
  name: 'StudentDashboard',
  data() {
    return {
      tab: 'drives',
      search: '',   
      branch: '',   
      min_cgpa: '',
      drives: [],
      applications: [],
      history: [],
      appliedDriveIds: [],

      searchQuery: '',
      branchFilter: '',
      cgpaFilter: '',
      message: '',
      error: '',
      selectedDrive: null,
      studentName: '',
      statusSteps: ['applied', 'shortlisted', 'interview', 'selected', 'placed']
    }
  },
  computed: {
    ...mapGetters('auth', ['currentUser'])
  },
  async mounted() {
    await this.loadAll()
    this.studentName = this.currentUser ? this.currentUser.email : ''
  },
  methods: {
    
    async loadAll() {
      try {
        this.drives = await studentService.getDrives({})
        this.applications = await studentService.getMyApplications()
        this.history = await studentService.getHistory()
        this.appliedDriveIds = this.applications.map(function(a) { return a.drive_id })
      } catch (err) {
        console.log('Error loading student data', err)
      }
    },

    async loadDrives() {
      try {
        this.drives = await studentService.getDrives({
          search: this.searchQuery,
          branch: this.branchFilter,
          min_cgpa: this.cgpaFilter
        })
      } catch (err) {
        console.log(err)
      }
    },

    async applyToDrive(driveId) {
      this.error = ''
      this.message = ''
      try {
        await studentService.applyToDrive(driveId)
        this.message = 'Application submitted successfully'
        await this.loadAll()
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to apply'
      }
    },

    alreadyApplied(driveId) {
      return this.appliedDriveIds.includes(driveId)
    },

    clearFilters() {
      this.searchQuery = ''
      this.branchFilter = ''
      this.cgpaFilter = ''
      this.loadDrives()
    },

    viewDrive(drive) {
      this.selectedDrive = drive
    },

    goToProfile() {
      this.$router.push('/student/profile')
    },

 

   
   
async exportCSV() {
  this.message = ''
  this.error = ''
  try {
    await studentService.triggerCsvExport()
    this.message = 'Export started! The CSV will be sent to your email shortly.'
  } catch (err) {
    this.error = err.response?.data?.message || 'Export failed. Make sure Celery is running.'
  }
},

async downloadConfirmation(applicationId) {
  try {
    await studentService.downloadConfirmation(applicationId)
  } catch (err) {
    this.error = 'Failed to download confirmation'
  }
},

  handleLogout() {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  localStorage.removeItem('user')
  this.$store.commit('auth/CLEAR_AUTH')
  this.$router.push('/login')
},

    statusBadge(status) {
      if (status === 'selected') return 'bg-success'
      if (status === 'shortlisted') return 'bg-info text-dark'
      if (status === 'applied') return 'bg-primary'
      if (status === 'rejected') return 'bg-danger'
      if (status === 'interview') return 'bg-warning text-dark'
      if (status === 'placed') return 'bg-success'
      return 'bg-secondary'
    },

    
   
    resultBadge(result) {
      if (result === 'passed') return 'bg-success'
      if (result === 'failed') return 'bg-danger'
      return 'bg-warning text-dark'
    },

    getStepClass(step, currentStatus) {
  const order = ['applied', 'shortlisted', 'interview', 'selected', 'placed']
  const currentIndex = order.indexOf(currentStatus)
  const stepIndex = order.indexOf(step)

  if (currentStatus === 'rejected') {
    return stepIndex === 0 ? 'bg-danger' : 'bg-light text-dark border'
  }
  if (stepIndex < currentIndex) return 'bg-success'
  if (stepIndex === currentIndex) return 'bg-primary'
  return 'bg-light text-dark border'
},
  
   


    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleDateString('en-IN')
    },

    formatLink(url) {
  if (!url) return '#'
  if (url.startsWith('http')) return url
  return 'https://' + url
},

    truncate(text) {
      if (!text) return ''
      return text.length > 100 ? text.substring(0, 100) + '...' : text
    }
  }
}
</script>