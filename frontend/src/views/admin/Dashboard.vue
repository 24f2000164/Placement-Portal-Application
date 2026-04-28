 <template>
  <div>
    <nav class="navbar navbar-dark bg-dark px-4">
  <span class="navbar-brand fw-bold">Placement Portal - Admin</span>
  <div class="d-flex gap-2">
    <button class="btn btn-outline-light btn-sm" @click="$router.push('/admin/charts')">Charts</button>
    <button class="btn btn-outline-light btn-sm" @click="$router.push('/ats')">ATS Checker</button>
    <button class="btn btn-outline-light btn-sm" @click="handleLogout">Logout</button>
  </div>
   </nav>

    <div class="container-fluid mt-4 px-4">

      <div class="row mb-4">
        <div class="col-12">
          <h4>Admin Dashboard</h4>
          <p class="text-muted">Welcome back, Admin</p>
        </div>
      </div>

      <div v-if="loadError" class="alert alert-danger">
        {{ loadError }}
      </div>

      <div class="row g-3 mb-4" v-if="stats">
        <div class="col-md-3">
          <div class="card border-primary">
            <div class="card-body text-center">
              <h2 class="text-primary">{{ stats.total_students }}</h2>
              <p class="mb-0">Total Students</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-success">
            <div class="card-body text-center">
              <h2 class="text-success">{{ stats.total_companies }}</h2>
              <p class="mb-0">Total Companies</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-warning">
            <div class="card-body text-center">
              <h2 class="text-warning">{{ stats.total_drives }}</h2>
              <p class="mb-0">Total Drives</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-info">
            <div class="card-body text-center">
              <h2 class="text-info">{{ stats.total_applications }}</h2>
              <p class="mb-0">Total Applications</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-secondary">
            <div class="card-body text-center">
              <h2 class="text-secondary">{{ stats.pending_companies }}</h2>
              <p class="mb-0">Pending Companies</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-secondary">
            <div class="card-body text-center">
              <h2 class="text-secondary">{{ stats.pending_drives }}</h2>
              <p class="mb-0">Pending Drives</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-success">
            <div class="card-body text-center">
              <h2 class="text-success">{{ stats.approved_companies }}</h2>
              <p class="mb-0">Approved Companies</p>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card border-danger">
            <div class="card-body text-center">
              <h2 class="text-danger">{{ stats.selected_students }}</h2>
              <p class="mb-0">Students Selected</p>
            </div>
          </div>
        </div>
      </div>

      <ul class="nav nav-tabs mb-4">
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'companies' }" href="#" @click.prevent="tab = 'companies'">Companies</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'students' }" href="#" @click.prevent="tab = 'students'">Students</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'drives' }" href="#" @click.prevent="tab = 'drives'">Drives</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'applications' }" href="#" @click.prevent="tab = 'applications'">Applications</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" :class="{ active: tab === 'logs' }" href="#" @click.prevent="tab = 'logs'">Logs</a>
        </li>
      </ul>

      <div v-if="message" class="alert alert-success alert-dismissible">
        {{ message }}
        <button type="button" class="btn-close" @click="message = ''"></button>
      </div>

      <div v-if="tab === 'companies'">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5>Registered Companies</h5>
          <input
            v-model="companySearch"
            type="text"
            class="form-control form-control-sm"
            placeholder="Search companies..."
            style="width: 220px"
            @input="searchCompanies"
          />
        </div>

        
        <div class="table-responsive">
          <table class="table table-bordered table-hover">
            <thead class="table-dark">
              <tr>
                <th>ID</th>
                <th>Company Name</th>
                <th>Industry</th>
                <th>Location</th>
                <th>HR Contact</th>
                <th>Status</th>
                <th>Drives</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="company in filteredCompanies" :key="company.id">
                <td>{{ company.id }}</td>
                <td>{{ company.company_name }}</td>
                <td>{{ company.industry }}</td>
                <td>{{ company.location }}</td>
                <td>{{ company.hr_contact }}</td>
                <td>
                  <span class="badge" :class="statusBadge(company.approval_status)">
                    {{ company.approval_status }}
                  </span>
                  <span v-if="company.is_blacklisted" class="badge bg-dark ms-1">Blacklisted</span>
                </td>
                <td>{{ company.drive_count }}</td>
                <td>
                  <div class="d-flex gap-1 flex-wrap">
                    <button v-if="company.approval_status === 'pending'" class="btn btn-success btn-sm" @click="approveCompany(company.id)">Approve</button>
                    <button v-if="company.approval_status === 'pending'" class="btn btn-danger btn-sm" @click="rejectCompany(company.id)">Reject</button>
                    <button v-if="!company.is_blacklisted" class="btn btn-dark btn-sm" @click="blacklistCompany(company.id)">Blacklist</button>
                    <button v-if="company.is_blacklisted" class="btn btn-secondary btn-sm" @click="unblacklistCompany(company.id)">Unblacklist</button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredCompanies.length === 0">
                <td colspan="8" class="text-center text-muted">No companies found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="tab === 'students'">
        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5>Registered Students</h5>
          <input
            v-model="studentSearch"
            type="text"
            class="form-control form-control-sm"
            placeholder="Search students..."
            style="width: 220px"
            @input="searchStudents"
          />
        </div>
        <div class="table-responsive">
          <table class="table table-bordered table-hover">
            <thead class="table-dark">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Branch</th>
                <th>CGPA</th>
                <th>Year</th>
                <th>Applications</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="student in filteredStudents" :key="student.id">
                <td>{{ student.id }}</td>
                <td>{{ student.full_name }}</td>
                <td>{{ student.email }}</td>
                <td>{{ student.branch }}</td>
                <td>{{ student.cgpa }}</td>
                <td>{{ student.year }}</td>
                <td>{{ student.application_count }}</td>
                <td>
                  <span v-if="student.is_blacklisted" class="badge bg-dark">Blacklisted</span>
                  <span v-else-if="!student.is_active" class="badge bg-secondary">Inactive</span>
                  <span v-else class="badge bg-success">Active</span>
                </td>
                <td>
                  <button v-if="!student.is_blacklisted" class="btn btn-dark btn-sm" @click="blacklistStudent(student.id)">Blacklist</button>
                  <button v-if="student.is_blacklisted" class="btn btn-secondary btn-sm" @click="unblacklistStudent(student.id)">Unblacklist</button>
                </td>
              </tr>
              <tr v-if="filteredStudents.length === 0">
                <td colspan="9" class="text-center text-muted">No students found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="tab === 'drives'">
        <h5 class="mb-3">All Placement Drives</h5>
        <div class="table-responsive">
          <table class="table table-bordered table-hover">
            <thead class="table-dark">
              <tr>
                <th>ID</th>
                <th>Company</th>
                <th>Job Title</th>
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
                <td>{{ drive.company_name }}</td>
                <td>{{ drive.job_title }}</td>
                <td>{{ formatDate(drive.application_deadline) }}</td>
                <td>{{ drive.min_cgpa }}</td>
                <td>{{ drive.applicant_count }}</td>
                <td>
                  <span class="badge" :class="statusBadge(drive.status)">{{ drive.status }}</span>
                </td>
                <td>
                  <div class="d-flex gap-1">
                    <button v-if="drive.status === 'pending'" class="btn btn-success btn-sm" @click="approveDrive(drive.id)">Approve</button>
                    <button v-if="drive.status === 'pending'" class="btn btn-danger btn-sm" @click="rejectDrive(drive.id)">Reject</button>
                    <span v-if="drive.status !== 'pending'" class="text-muted small">No action</span>
                  </div>
                </td>
              </tr>
              <tr v-if="drives.length === 0">
                <td colspan="8" class="text-center text-muted">No drives found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="tab === 'applications'">
        <h5 class="mb-3">All Student Applications</h5>
        <div class="table-responsive">
          <table class="table table-bordered table-hover">
            <thead class="table-dark">
              <tr>
                <th>ID</th>
                <th>Student</th>
                <th>Company</th>
                <th>Drive</th>
                <th>Applied On</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications" :key="app.id">
                <td>{{ app.id }}</td>
                <td>{{ app.student_name }}</td>
                <td>{{ app.company_name }}</td>
                <td>{{ app.drive_title }}</td>
                <td>{{ formatDate(app.applied_at) }}</td>
                <td>
                  <span class="badge" :class="appStatusBadge(app.status)">{{ app.status }}</span>
                </td>
              </tr>
              <tr v-if="applications.length === 0">
                <td colspan="6" class="text-center text-muted">No applications found</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-if="tab === 'logs'">
        <h5 class="mb-3">Admin Action Logs</h5>
        <div class="table-responsive">
          <table class="table table-bordered table-hover">
            <thead class="table-dark">
              <tr>
                <th>ID</th>
                <th>Action</th>
                <th>Target Type</th>
                <th>Target ID</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="log in logs" :key="log.id">
                <td>{{ log.id }}</td>
                <td>{{ log.action }}</td>
                <td>{{ log.target_type }}</td>
                <td>{{ log.target_id }}</td>
                <td>{{ formatDate(log.timestamp) }}</td>
              </tr>
              <tr v-if="logs.length === 0">
                <td colspan="5" class="text-center text-muted">No logs yet</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import adminService from '@/services/adminService'

export default {
  name: 'AdminDashboard',
  data() {
    return {
      tab: 'companies',
      stats: null,
      companies: [],
      students: [],
      drives: [],
      applications: [],
      logs: [],
      companySearch: '',
      studentSearch: '',
      filteredCompanies: [],
      filteredStudents: [],
      message: '',
      loadError: ''
    }
  },
  async mounted() {
    await this.loadAll()
  },
  methods: {
    async loadAll() {
      this.loadError = ''
      try {
        this.stats = await adminService.getDashboardStats()
        this.companies = await adminService.getAllCompanies()
        this.filteredCompanies = this.companies
        this.students = await adminService.getAllStudents()
        this.filteredStudents = this.students
        this.drives = await adminService.getAllDrives()
        this.applications = await adminService.getAllApplications()
        this.logs = await adminService.getLogs()
      } catch (err) {
        console.log('Error loading admin data:', err)
        this.loadError = 'Failed to load data. Make sure Flask is running.'
      }
    },

    async searchCompanies() {
      if (!this.companySearch.trim()) {
        this.filteredCompanies = this.companies
        return
      }
      try {
        this.filteredCompanies = await adminService.searchCompanies(this.companySearch)
      } catch (err) {
        console.log(err)
      }
    },

    async searchStudents() {
      if (!this.studentSearch.trim()) {
        this.filteredStudents = this.students
        return
      }
      try {
        this.filteredStudents = await adminService.searchStudents(this.studentSearch)
      } catch (err) {
        console.log(err)
      }
    },

    async approveCompany(id) {
      await adminService.approveCompany(id)
      this.message = 'Company approved successfully'
      await this.loadAll()
    },

    async rejectCompany(id) {
      await adminService.rejectCompany(id)
      this.message = 'Company rejected'
      await this.loadAll()
    },

    async blacklistCompany(id) {
      await adminService.blacklistCompany(id)
      this.message = 'Company blacklisted and all drives closed'
      await this.loadAll()
    },

    async unblacklistCompany(id) {
      await adminService.unblacklistCompany(id)
      this.message = 'Company unblacklisted'
      await this.loadAll()
    },

    async blacklistStudent(id) {
      await adminService.blacklistStudent(id)
      this.message = 'Student blacklisted'
      await this.loadAll()
    },

    async unblacklistStudent(id) {
      await adminService.unblacklistStudent(id)
      this.message = 'Student unblacklisted'
      await this.loadAll()
    },

    async approveDrive(id) {
      await adminService.approveDrive(id)
      this.message = 'Drive approved successfully'
      await this.loadAll()
    },

    async rejectDrive(id) {
      await adminService.rejectDrive(id)
      this.message = 'Drive rejected'
      await this.loadAll()
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
      if (status === 'rejected') return 'bg-danger'
      if (status === 'closed') return 'bg-secondary'
      return 'bg-secondary'
    },

    appStatusBadge(status) {
      if (status === 'selected') return 'bg-success'
      if (status === 'shortlisted') return 'bg-info text-dark'
      if (status === 'applied') return 'bg-primary'
      if (status === 'rejected') return 'bg-danger'
      if (status === 'interview') return 'bg-warning text-dark'
      return 'bg-secondary'
    },

    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      return new Date(dateStr).toLocaleDateString('en-IN')
    }
  }
}
</script>













