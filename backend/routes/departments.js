const express = require('express');
const router = express.Router();
const db = require('../config/database');

router.get('/', async (req, res) => {
  try {
    const [rows] = await db.execute(`
      SELECT d.*, e.EmployeeName AS ManagerName
      FROM Department d
      LEFT JOIN Employee e ON d.ManagerID = e.EmployeeID
      ORDER BY d.DepartmentName
    `);
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const { DepartmentName, ManagerID } = req.body;
    if (!DepartmentName) return res.status(400).json({ error: 'DepartmentName required' });
    const [result] = await db.execute('INSERT INTO Department (DepartmentName, ManagerID) VALUES (?, ?)',
      [DepartmentName, ManagerID || null]);
    res.status(201).json({ DepartmentID: result.insertId, message: 'Department created' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const { DepartmentName, ManagerID } = req.body;
    await db.execute('UPDATE Department SET DepartmentName = ?, ManagerID = ? WHERE DepartmentID = ?',
      [DepartmentName, ManagerID || null, req.params.id]);
    res.json({ message: 'Department updated' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const [result] = await db.execute('DELETE FROM Department WHERE DepartmentID = ?', [req.params.id]);
    if (result.affectedRows === 0) return res.status(404).json({ error: 'Department not found' });
    res.json({ message: 'Department deleted' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;

