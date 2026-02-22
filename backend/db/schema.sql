PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS contracts (
  project_id TEXT PRIMARY KEY,
  project_name TEXT NOT NULL,
  original_contract_value REAL NOT NULL,
  contract_date TEXT,
  substantial_completion_date TEXT,
  retention_pct REAL,
  payment_terms TEXT,
  gc_name TEXT,
  architect TEXT,
  engineer_of_record TEXT
);

CREATE TABLE IF NOT EXISTS sov (
  project_id TEXT NOT NULL,
  sov_line_id TEXT PRIMARY KEY,
  line_number INTEGER,
  description TEXT,
  scheduled_value REAL,
  labor_pct REAL,
  material_pct REAL,
  FOREIGN KEY(project_id) REFERENCES contracts(project_id)
);

CREATE TABLE IF NOT EXISTS sov_budget (
  project_id TEXT NOT NULL,
  sov_line_id TEXT PRIMARY KEY,
  estimated_labor_hours REAL,
  estimated_labor_cost REAL,
  estimated_material_cost REAL,
  estimated_equipment_cost REAL,
  estimated_sub_cost REAL,
  productivity_factor REAL,
  key_assumptions TEXT,
  FOREIGN KEY(project_id) REFERENCES contracts(project_id),
  FOREIGN KEY(sov_line_id) REFERENCES sov(sov_line_id)
);

CREATE TABLE IF NOT EXISTS labor_logs (
  project_id TEXT NOT NULL,
  log_id TEXT,
  date TEXT,
  employee_id TEXT,
  role TEXT,
  sov_line_id TEXT,
  hours_st REAL,
  hours_ot REAL,
  hourly_rate REAL,
  burden_multiplier REAL,
  work_area TEXT,
  cost_code TEXT,
  FOREIGN KEY(project_id) REFERENCES contracts(project_id),
  FOREIGN KEY(sov_line_id) REFERENCES sov(sov_line_id)
);

CREATE TABLE IF NOT EXISTS material_deliveries (
  project_id TEXT NOT NULL,
  delivery_id TEXT,
  date TEXT,
  sov_line_id TEXT,
  material_category TEXT,
  item_description TEXT,
  quantity REAL,
  unit TEXT,
  unit_cost REAL,
  total_cost REAL,
  po_number TEXT,
  vendor TEXT,
  received_by TEXT,
  condition_notes TEXT,
  FOREIGN KEY(project_id) REFERENCES contracts(project_id),
  FOREIGN KEY(sov_line_id) REFERENCES sov(sov_line_id)
);

CREATE TABLE IF NOT EXISTS billing_history (
  project_id TEXT NOT NULL,
  application_number INTEGER,
  period_end TEXT,
  period_total REAL,
  cumulative_billed REAL,
  retention_held REAL,
  net_payment_due REAL,
  status TEXT,
  payment_date TEXT,
  line_item_count INTEGER,
  PRIMARY KEY(project_id, application_number),
  FOREIGN KEY(project_id) REFERENCES contracts(project_id)
);

CREATE TABLE IF NOT EXISTS billing_line_items (
  sov_line_id TEXT,
  description TEXT,
  scheduled_value REAL,
  previous_billed REAL,
  this_period REAL,
  total_billed REAL,
  pct_complete REAL,
  balance_to_finish REAL,
  project_id TEXT,
  application_number INTEGER,
  FOREIGN KEY(project_id) REFERENCES contracts(project_id),
  FOREIGN KEY(sov_line_id) REFERENCES sov(sov_line_id)
);

CREATE TABLE IF NOT EXISTS change_orders (
  project_id TEXT,
  co_number TEXT,
  date_submitted TEXT,
  reason_category TEXT,
  description TEXT,
  amount REAL,
  status TEXT,
  related_rfi TEXT,
  affected_sov_lines TEXT,
  labor_hours_impact REAL,
  schedule_impact_days REAL,
  submitted_by TEXT,
  approved_by TEXT,
  PRIMARY KEY(project_id, co_number),
  FOREIGN KEY(project_id) REFERENCES contracts(project_id)
);

CREATE TABLE IF NOT EXISTS rfis (
  project_id TEXT,
  rfi_number TEXT,
  date_submitted TEXT,
  subject TEXT,
  submitted_by TEXT,
  assigned_to TEXT,
  priority TEXT,
  status TEXT,
  date_required TEXT,
  date_responded TEXT,
  response_summary TEXT,
  cost_impact TEXT,
  schedule_impact TEXT,
  PRIMARY KEY(project_id, rfi_number),
  FOREIGN KEY(project_id) REFERENCES contracts(project_id)
);

CREATE TABLE IF NOT EXISTS field_notes (
  project_id TEXT,
  note_id TEXT,
  date TEXT,
  author TEXT,
  note_type TEXT,
  content TEXT,
  photos_attached INTEGER,
  weather TEXT,
  temp_high REAL,
  temp_low REAL,
  FOREIGN KEY(project_id) REFERENCES contracts(project_id)
);

CREATE TABLE IF NOT EXISTS computed_sov_metrics (
  project_id TEXT,
  sov_line_id TEXT,
  line_number INTEGER,
  description TEXT,
  scheduled_value REAL,
  estimated_labor_cost REAL,
  estimated_material_cost REAL,
  estimated_equipment_cost REAL,
  estimated_sub_cost REAL,
  bid_max_cost REAL,
  actual_labor_cost REAL,
  actual_material_cost REAL,
  billing_total REAL,
  billing_lag REAL,
  rejected_co_exposure REAL,
  labor_overrun_pct REAL,
  material_variance_pct REAL,
  overrun_amount REAL,
  overrun_pct REAL,
  PRIMARY KEY(project_id, sov_line_id)
);

CREATE TABLE IF NOT EXISTS computed_project_metrics (
  project_id TEXT PRIMARY KEY,
  project_name TEXT,
  contract_value REAL,
  total_estimated_cost REAL,
  total_actual_labor_cost REAL,
  total_actual_material_cost REAL,
  total_actual_cost REAL,
  bid_margin_pct REAL,
  realized_margin_pct REAL,
  margin_erosion_pct REAL,
  pending_co_exposure REAL,
  approved_co_total REAL,
  rejected_co_total REAL,
  billing_lag REAL,
  open_rfis INTEGER,
  overdue_rfis INTEGER,
  orphan_rfis INTEGER,
  health_score REAL,
  status TEXT,
  exceedance_lines INTEGER,
  total_lines INTEGER
);

CREATE TABLE IF NOT EXISTS triggers (
  trigger_id TEXT PRIMARY KEY,
  project_id TEXT,
  date TEXT,
  type TEXT,
  severity TEXT,
  value REAL,
  threshold REAL,
  details TEXT,
  affected_sov_lines TEXT
);

CREATE TABLE IF NOT EXISTS dossiers (
  project_id TEXT PRIMARY KEY,
  dossier_json TEXT NOT NULL,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_labor_project_date ON labor_logs(project_id, date);
CREATE INDEX IF NOT EXISTS idx_labor_sov ON labor_logs(sov_line_id);
CREATE INDEX IF NOT EXISTS idx_mat_project_date ON material_deliveries(project_id, date);
CREATE INDEX IF NOT EXISTS idx_billing_project ON billing_history(project_id, application_number);
CREATE INDEX IF NOT EXISTS idx_rfi_project ON rfis(project_id, date_submitted);
CREATE INDEX IF NOT EXISTS idx_field_project ON field_notes(project_id, date);
CREATE INDEX IF NOT EXISTS idx_triggers_project ON triggers(project_id, date);
