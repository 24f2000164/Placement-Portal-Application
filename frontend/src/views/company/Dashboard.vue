
<template>
  <div>
    <nav class="navbar navbar-dark bg-success px-4">
      <span class="navbar-brand fw-bold">Placement Portal - Company</span>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-light btn-sm" @click="$router.push('/company/profile')">Profile</button>
        <button class="btn btn-outline-light btn-sm" @click="handleLogout">Logout</button>

        <button class="btn btn-outline-light btn-sm" @click="$router.push('/ats')">ATS Checker</button>


        
      </div>
    </nav>
<div v-if="loadError" class="alert alert-danger mx-4 mt-3">{{ loadError }}</div>
    <div class="container-fluid mt-4 px-4">

      <div v-if="!isApproved" class="alert alert-warning">
        Your company registration is pending admin approval. You cannot create drives until approved.
      </div>

      <div class="row mb-3">
        <div class="col">
          <h4>Welcome to Career and Placement Cell 🎓</h4>
          <h5 class="text-muted">{{ stats ? stats.company_name : '' }}</h5>
          <span class="badge" :class="approvalBadge">{{ stats ? stats.approval_status : '' }}</span>
        </div>
      </div>
 


  <div class="row g-3 mb-4" v-if="stats">
  <div class="col-md-2">
    <div class="card border-primary text-center">
      <div class="card-body">
        <h2 class="text-primary">{{ stats.total_drives }}</h2>
        <p class="mb-0 small">Total Drives</p>
      </div>
    </div>
  </div>
  <div class="col-md-2">
    <div class="card border-success text-center">
      <div class="card-body">
        <h2 class="text-success">{{ stats.approved_drives }}</h2>
        <p class="mb-0 small">Approved</p>
      </div>
    </div>
  </div>
  <div class="col-md-2">
    <div class="card border-warning text-center">
      <div class="card-body">
        <h2 class="text-warning">{{ stats.pending_drives }}</h2>
        <p class="mb-0 small">Pending</p>
      </div>
    </div>
  </div>
  <div class="col-md-2">
    <div class="card border-danger text-center">
      <div class="card-body">
        <h2 class="text-danger">{{ stats.rejected_drives || 0 }}</h2>
        <p class="mb-0 small">Rejected</p>
      </div>
    </div>
  </div>
  <div class="col-md-2">
    <div class="card border-secondary text-center">
      <div class="card-body">
        <h2 class="text-secondary">{{ stats.closed_drives }}</h2>
        <p class="mb-0 small">Closed</p>
      </div>
    </div>
  </div>
  <div class="col-md-2">
    <div class="card border-info text-center">
      <div class="card-body">
        <h2 class="text-info">{{ stats.total_applicants }}</h2>
        <p class="mb-0 small">Applicants</p>
      </div>
    </div>
  </div>
</div>

      <ul class="nav nav-tabs mb-4">
        <div class="d-flex justify-content-between align-items-center mb-2">
  <ul class="nav nav-tabs flex-grow-1">
    <li class="nav-item">
      <a class="nav-link" :class="{ active: tab === 'drives' }" href="#" @click.prevent="tab = 'drives'">My Drives</a>
    </li>
    <li class="nav-item">
      <a class="nav-link" :class="{ active: tab === 'create' }" href="#" @click.prevent="tab = 'create'">Create Drive</a>
    </li>
    <li class="nav-item" v-if="selectedDriveId">
      <a class="nav-link" :class="{ active: tab === 'applicants' }" href="#" @click.prevent="tab = 'applicants'">Applicants</a>
    </li>
  </ul>
  
</div>
         
        <li class="nav-item" v-if="selectedDriveId">
          <a class="nav-link" :class="{ active: tab === 'applicants' }" href="#" @click.prevent="tab = 'applicants'">
            Applicants
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
        


        <!-- Add next to "My Placement Drives" heading -->
<div class="d-flex justify-content-between align-items-center mb-3">
  <h5>My Placement Drives</h5>
  <button class="btn btn-success btn-sm" @click="exportCSV">
    Export Applications CSV
  </button>
</div>

        <div v-if="drives.length === 0" class="text-center py-4 text-muted">
          No drives created yet. Go to Create Drive tab to add one.
        </div>

        <div class="table-responsive" v-else>
          <table class="table table-bordered table-hover">
            <thead class="table-dark">
              <tr>
                <th>ID</th>
                <th>Job Title</th>
                <th>Location</th>
                <th>Deadline</th>
                <th>Min CGPA</th>
                <th>Applicants</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="drive in drives" :key="drive.id">
                <td>{{ drive.id }}</td>
                <td>{{ drive.job_title }}</td>
                <td>{{ drive.location }}</td>
                <td>{{ formatDate(drive.application_deadline) }}</td>
                <td>{{ drive.min_cgpa }}</td>
                <td>{{ drive.applicant_count }}</td>
                <td>
                  <span class="badge" :class="statusBadge(drive.status)">{{ drive.status }}</span>
                </td>
                <td>
                  <div class="d-flex gap-1 flex-wrap">
                    <button
                      class="btn btn-info btn-sm"
                      @click="viewApplicants(drive.id)"
                    >Applicants</button>
                    <button
                         v-if="drive.status === 'approved' || drive.status === 'pending'"
                         class="btn btn-warning btn-sm"
                         @click="editDrive(drive)"
                       >Edit</button>
                       <button
                         v-if="drive.status === 'approved'"
                         class="btn btn-secondary btn-sm"
                         @click="closeDrive(drive.id)"
                       >Close</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="editingDrive" class="card mt-4">
          <div class="card-header d-flex justify-content-between">
            <strong>Edit Drive - {{ editingDrive.job_title }}</strong>
            <button class="btn btn-sm btn-outline-secondary" @click="editingDrive = null">Cancel</button>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Job Title</label>
                <input v-model="editForm.job_title" type="text" class="form-control" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Salary</label>
                <input v-model="editForm.salary" type="text" class="form-control" placeholder="e.g. 12 LPA" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Location</label>
                <input v-model="editForm.location" type="text" class="form-control" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Application Deadline</label>
                <input v-model="editForm.application_deadline" type="date" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Eligible Branches</label>
                <input v-model="editForm.eligible_branches" type="text" class="form-control" placeholder="CSE,ECE,IT" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Min CGPA</label>
                <input v-model="editForm.min_cgpa" type="number" step="0.1" min="0" max="10" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Eligible Year</label>
                <select v-model="editForm.eligible_year" class="form-select">
                  <option value="">All Years</option>
                  <option value="1">1st Year</option>
                  <option value="2">2nd Year</option>
                  <option value="3">3rd Year</option>
                  <option value="4">4th Year</option>
                </select>
              </div>
              <div class="col-12">
                <label class="form-label">Skills Required</label>
                <input v-model="editForm.skills_required" type="text" class="form-control" placeholder="Python, Java, SQL" />
              </div>
              <div class="col-12">
                <label class="form-label">Job Description</label>
                <textarea v-model="editForm.job_description" class="form-control" rows="3"></textarea>
              </div>
            </div>
            <button class="btn btn-primary mt-3" @click="saveEdit">Save Changes</button>
          </div>
        </div>
      </div>

      <div v-if="tab === 'create'">
        <div class="card" style="max-width: 700px;">
          <div class="card-header">
            <strong>Create New Placement Drive</strong>
          </div>
          <div class="card-body">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label">Job Title <span class="text-danger">*</span></label>
                <input v-model="createForm.job_title" type="text" class="form-control" placeholder="e.g. Software Engineer" required />
              </div>
              <div class="col-md-6">
                <label class="form-label">Salary</label>
                <input v-model="createForm.salary" type="text" class="form-control" placeholder="e.g. 12 LPA" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Location</label>
                <input v-model="createForm.location" type="text" class="form-control" placeholder="City or Remote" />
              </div>
              <div class="col-md-6">
                <label class="form-label">Application Deadline</label>
                <input v-model="createForm.application_deadline" type="date" class="form-control" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Eligible Branches</label>
                <input v-model="createForm.eligible_branches" type="text" class="form-control" placeholder="CSE,ECE,IT" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Min CGPA</label>
                <input v-model="createForm.min_cgpa" type="number" step="0.1" min="0" max="10" class="form-control" placeholder="e.g. 7.0" />
              </div>
              <div class="col-md-4">
                <label class="form-label">Eligible Year</label>
                <select v-model="createForm.eligible_year" class="form-select">
                  <option value="">All Years</option>
                  <option value="1">1st Year</option>
                  <option value="2">2nd Year</option>
                  <option value="3">3rd Year</option>
                  <option value="4">4th Year</option>
                </select>
              </div>
              <div class="col-12">
                <label class="form-label">Skills Required</label>
                <input v-model="createForm.skills_required" type="text" class="form-control" placeholder="Python, Java, SQL (comma separated)" />
              </div>
              <div class="col-12">
                <label class="form-label">Job Description</label>
                <textarea v-model="createForm.job_description" class="form-control" rows="4" placeholder="Describe the role and responsibilities"></textarea>
              </div>
            </div>
            <button
              class="btn btn-success mt-3"
              @click="submitDrive"
              :disabled="submitting || !isApproved"
            >
              {{ submitting ? 'Creating...' : 'Create Drive' }}
            </button>
            <p v-if="!isApproved" class="text-danger mt-2 small">
              You must be approved by admin before creating drives.
            </p>
          </div>
        </div>
      </div>

      <div v-if="tab === 'applicants'">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5>Applicants for Drive #{{ selectedDriveId }}</h5>
          <button class="btn btn-sm btn-outline-secondary" @click="tab = 'drives'">Back to Drives</button>
        </div>

        <div v-if="applicants.length === 0" class="text-center py-4 text-muted">
          No applicants yet for this drive.
        </div>

        <div v-for="app in applicants" :key="app.id" class="card mb-3">
          <div class="card-body">
            <div class="row align-items-center">
              <div class="col-md-4">
                <h6 class="mb-1">{{ app.student_details ? app.student_details.full_name : 'N/A' }}</h6>
                <p class="text-muted small mb-1">{{ app.student_details ? app.student_details.email : '' }}</p>
                <p class="small mb-1">
                  Branch: {{ app.student_details ? app.student_details.branch : 'N/A' }} |
                  CGPA: {{ app.student_details ? app.student_details.cgpa : 'N/A' }} |
                  Year: {{ app.student_details ? app.student_details.year : 'N/A' }}
                </p>
                <p class="small mb-0">Skills: {{ app.student_details ? app.student_details.skills : 'N/A' }}</p>
              </div>

              <div class="col-md-3">
                <p class="small mb-1">Applied: {{ formatDate(app.applied_at) }}</p>
                <span class="badge" :class="statusBadge(app.status)">{{ app.status }}</span>
              </div>

              <div class="col-md-2">
                <label class="form-label small mb-1">Update Status</label>
                <select
                  class="form-select form-select-sm"
                  :value="app.status"
                  @change="updateStatus(app.id, $event.target.value)"
                >
                  <option value="applied">Applied</option>
                  <option value="shortlisted">Shortlisted</option>
                  <option value="interview">Interview</option>
                  <option value="selected">Selected</option>
                  <option value="rejected">Rejected</option>
                  <option value="placed">Placed</option>
                </select>
              </div>

              <div class="col-md-3">
              <label class="form-label small mb-1">Feedback / Reason</label>
              <input
               type="text"
                class="form-control form-control-sm"
                placeholder="Optional feedback..."
                v-model="app.feedbackInput"
                @blur="saveFeedback(app.id, app.feedbackInput)"
              />
            </div>

              <div class="col-md-3">
                <div v-if="app.interview" class="small">
                  <p class="mb-1">Interview: {{ app.interview.mode }}</p>
                  <p class="mb-1">Date: {{ formatDate(app.interview.scheduled_at) }}</p>
                  <p class="mb-0">Result: {{ app.interview.result }}</p>
                </div>
                <button
                  class="btn btn-outline-primary btn-sm mt-1"
                  @click="openInterviewModal(app)"
                >
                  {{ app.interview ? 'Edit Interview' : 'Schedule Interview' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <div v-if="interviewModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Schedule Interview</h5>
            <button type="button" class="btn-close" @click="interviewModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Interview Mode</label>
              <select v-model="interviewForm.mode" class="form-select">
                <option value="In-person">In-person</option>
                <option value="Online">Online</option>
                <option value="Telephonic">Telephonic</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Date and Time</label>
              <input v-model="interviewForm.scheduled_at" type="datetime-local" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">Venue / Link</label>
              <input v-model="interviewForm.venue" type="text" class="form-control" placeholder="Office address or meeting link" />
            </div>
            <div class="mb-3">
              <label class="form-label">Notes</label>
              <textarea v-model="interviewForm.notes" class="form-control" rows="2" placeholder="Any instructions for candidate"></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Result</label>
              <select v-model="interviewForm.result" class="form-select">
                <option value="pending">Pending</option>
                <option value="passed">Passed</option>
                <option value="failed">Failed</option>
              </select>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-primary" @click="submitInterview">Save Interview</button>
            <button class="btn btn-secondary" @click="interviewModal = false">Cancel</button>
          </div>
        </div>
      </div>
    </div>


  </div>
</template>

<script>
import { mapActions } from 'vuex'
import companyService from '@/services/companyService'
import api from '@/services/api'

export default {
  name: 'CompanyDashboard',
  data() {
    return {
      tab: 'drives',
      stats: null,
      drives: [],
      applicants: [],

      selectedDriveId: null,
      editingDrive: null,
      interviewModal: false,
      selectedApplicationId: null,
      message: '',
      error: '',
      loadError: '',
      submitting: false,
      createForm: {
        job_title: '',
        job_description: '',
        salary: '',
        location: '',
        eligible_branches: '',
        min_cgpa: '',
        eligible_year: '',
        skills_required: '',
        application_deadline: ''
      },
      editForm: {},
      interviewForm: {
        mode: 'In-person',
        scheduled_at: '',
        venue: '',
        notes: '',
        result: 'pending'
      }
    }
  },
  computed: {
    isApproved() {
      return this.stats && this.stats.approval_status === 'approved'
    },
    approvalBadge() {
      if (!this.stats) return 'bg-secondary'
      if (this.stats.approval_status === 'approved') return 'bg-success'
      if (this.stats.approval_status === 'pending') return 'bg-warning text-dark'
      return 'bg-danger'
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    ...mapActions('auth', ['logout']),

    
  async loadData() {
  this.loadError = ''
  try {
    this.stats = await companyService.getDashboard()
    this.drives = await companyService.getDrives()
  } catch (err) {
    console.log('Error loading company data', err)
    this.loadError = 'Failed to load data. Make sure Flask is running.'
  }
},

    async viewApplicants(driveId) {
      this.selectedDriveId = driveId
      try {
        this.applicants = await companyService.getApplicants(driveId)
        this.tab = 'applicants'
      } catch (err) {
        this.error = 'Failed to load applicants'
      }
    },

    async submitDrive() {
      if (!this.createForm.job_title) {
        this.error = 'Job title is required'
        return
      }
      this.submitting = true
      this.message = ''
      this.error = ''
      try {
        await companyService.createDrive(this.createForm)
        this.message = 'Drive created successfully. Awaiting admin approval.'
        this.createForm = {
          job_title: '',
          job_description: '',
          salary: '',
          location: '',
          eligible_branches: '',
          min_cgpa: '',
          eligible_year: '',
          skills_required: '',
          application_deadline: ''
        }
        await this.loadData()
        this.tab = 'drives'
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to create drive'
      } finally {
        this.submitting = false
      }
    },

    editDrive(drive) {
      this.editingDrive = drive
      this.editForm = {
        job_title: drive.job_title,
        job_description: drive.job_description,
        salary: drive.salary,
        location: drive.location,
        eligible_branches: drive.eligible_branches,
        min_cgpa: drive.min_cgpa,
        eligible_year: drive.eligible_year,
        skills_required: drive.skills_required,
        application_deadline: drive.application_deadline ? drive.application_deadline.substring(0, 10) : ''
      }
    },

    async saveEdit() {
      this.message = ''
      this.error = ''
      try {
        await companyService.updateDrive(this.editingDrive.id, this.editForm)
        this.message = 'Drive updated successfully'
        this.editingDrive = null
        await this.loadData()
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to update drive'
      }
    },

    async closeDrive(driveId) {
  this.message = ''
  this.error = ''
  try {
    await companyService.closeDrive(driveId)
    this.message = 'Drive closed successfully'
    this.editingDrive = null
    await this.loadData()
  } catch (err) {
    this.error = err.response?.data?.message || 'Failed to close drive'
  }
},

    async updateStatus(applicationId, status) {
      this.message = ''
      this.error = ''
      try {
        await companyService.updateApplicationStatus(applicationId, status)
        this.message = 'Application status updated'
        await this.viewApplicants(this.selectedDriveId)
        await this.loadData()
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to update status'
      }
    },


    openInterviewModal(app) {
      this.selectedApplicationId = app.id
      if (app.interview) {
        this.interviewForm = {
          mode: app.interview.mode || 'In-person',
          scheduled_at: app.interview.scheduled_at ? app.interview.scheduled_at.substring(0, 16) : '',
          venue: app.interview.venue || '',
          notes: app.interview.notes || '',
          result: app.interview.result || 'pending'
        }
      } else {
        this.interviewForm = {
          mode: 'In-person',
          scheduled_at: '',
          venue: '',
          notes: '',
          result: 'pending'
        }
      }
      this.interviewModal = true
    },

    async submitInterview() {
      this.message = ''
      this.error = ''
      try {
        await companyService.scheduleInterview(this.selectedApplicationId, this.interviewForm)
        this.message = 'Interview scheduled successfully'
        this.interviewModal = false
        await this.viewApplicants(this.selectedDriveId)
        await this.loadData()
      } catch (err) {
        this.error = err.response?.data?.message || 'Failed to schedule interview'
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
      if (status === 'approved') return 'bg-success'
      if (status === 'pending') return 'bg-warning text-dark'
      if (status === 'closed') return 'bg-secondary'
      if (status === 'selected') return 'bg-success'
      if (status === 'shortlisted') return 'bg-info text-dark'
      if (status === 'applied') return 'bg-primary'
      if (status === 'rejected') return 'bg-danger'
      if (status === 'interview') return 'bg-warning text-dark'
      if (status === 'placed') return 'bg-success'
      return 'bg-secondary'
    },

    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleDateString('en-IN')
    },
 async exportCSV() {
  this.message = ''
  this.error = ''
  try {
    await companyService.triggerCsvExport()
    this.message = 'Export started! The CSV will be sent to your email shortly.'
  } catch (err) {
    this.error = err.response?.data?.message || 'Export failed. Make sure Celery is running.'
  }
},

  async saveFeedback(applicationId, feedback) {
  if (!feedback || !feedback.trim()) return
  try {
    await companyService.updateApplicationStatus(applicationId, null, feedback)
    this.message = 'Feedback saved'
  } catch (err) {
    console.log('Feedback save error', err)
  }
},

  }
}
</script>