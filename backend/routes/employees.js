const express = require('express');
const router = express.Router();
const db = require('../config/database');

router.get('/', async (req, res) => {
  try {
    const [rows] = await db.execute(`
      SELECT e.*, r.Title AS RoleTitle, b.BranchName, d.DepartmentName, m.EmployeeName AS ManagerName
      FROM Employee e
      LEFT JOIN Role r ON e.RoleID = r.RoleID
      LEFT JOIN Branch b ON e.BranchID = b.BranchID
      LEFT JOIN Department d ON e.DepartmentID = d.DepartmentID
      LEFT JOIN Employee m ON e.ManagerID = m.EmployeeID
      ORDER BY e.EmployeeName
    `);
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const { EmployeeName, RoleID, Salary, BranchID, DepartmentID, ManagerID, HireDate, Email, PhoneNumber } = req.body;
    if (!EmployeeName || !RoleID || !Salary || !BranchID || !DepartmentID || !HireDate) {
      return res.status(400).json({ error: 'Required fields missing' });
    }
    const [result] = await db.execute(
      `INSERT INTO Employee (EmployeeName, RoleID, Salary, BranchID, DepartmentID, ManagerID, HireDate, Email, PhoneNumber)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [EmployeeName, RoleID, Salary, BranchID, DepartmentID, ManagerID || null, HireDate, Email || null, PhoneNumber || null]
    );
    res.status(201).json({ EmployeeID: result.insertId, message: 'Employee created' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const { EmployeeName, RoleID, Salary, BranchID, DepartmentID, ManagerID, HireDate, Email, PhoneNumber } = req.body;
    await db.execute(
      `UPDATE Employee SET EmployeeName = ?, RoleID = ?, Salary = ?, BranchID = ?, DepartmentID = ?,
       ManagerID = ?, HireDate = ?, Email = ?, PhoneNumber = ? WHERE EmployeeID = ?`,
      [EmployeeName, RoleID, Salary, BranchID, DepartmentID, ManagerID || null, HireDate, Email || null, PhoneNumber || null, req.params.id]
    );
    res.json({ message: 'Employee updated' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const [result] = await db.execute('DELETE FROM Employee WHERE EmployeeID = ?', [req.params.id]);
    if (result.affectedRows === 0) return res.status(404).json({ error: 'Employee not found' });
    res.json({ message: 'Employee deleted' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;

