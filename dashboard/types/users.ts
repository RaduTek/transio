export type EmployeeRole =
  | 'Driver'
  | 'Dispatcher'
  | 'Controller'
  | 'Manager'
  | 'Sales'
  | 'Support'
  | 'Technician'
  | 'Mechanic'
  | 'Other'

export interface Employee {
  id: string
  email: string
  phone: string
  first_name: string
  last_name: string
  active: boolean
  role: EmployeeRole
  customer_id: string
  employment_start_date: string
}
