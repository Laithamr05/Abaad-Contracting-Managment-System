const express = require('express');
const router = express.Router();
const db = require('../config/database');

router.get('/', async (req, res) => {
  try {
    const [rows] = await db.execute(`
      SELECT b.*, e.EmployeeName AS ManagerName
      FROM Branch b
      LEFT JOIN BranchManager bm ON b.BranchID = bm.BranchID
      LEFT JOIN Employee e ON bm.EmployeeID = e.EmployeeID
      ORDER BY b.BranchName
    `);
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const [rows] = await db.execute('SELECT * FROM Branch WHERE BranchID = ?', [req.params.id]);
    if (rows.length === 0) return res.status(404).json({ error: 'Branch not found' });
    res.json(rows[0]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const { BranchName, City, Address, PhoneNumber, ManagerID } = req.body;
    if (!BranchName || !City) return res.status(400).json({ error: 'BranchName and City required' });
    const [result] = await db.execute(
      'INSERT INTO Branch (BranchName, City, Address, PhoneNumber) VALUES (?, ?, ?, ?)',
      [BranchName, City, Address || null, PhoneNumber || null]
    );
    if (ManagerID) {
      await db.execute('INSERT INTO BranchManager (BranchID, EmployeeID, AssignedDate) VALUES (?, ?, CURDATE())',
        [result.insertId, ManagerID]);
    }
    res.status(201).json({ BranchID: result.insertId, message: 'Branch created' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const { BranchName, City, Address, PhoneNumber, ManagerID } = req.body;
    await db.execute('UPDATE Branch SET BranchName = ?, City = ?, Address = ?, PhoneNumber = ? WHERE BranchID = ?',
      [BranchName, City, Address || null, PhoneNumber || null, req.params.id]);
    if (ManagerID) {
      await db.execute('DELETE FROM BranchManager WHERE BranchID = ?', [req.params.id]);
      await db.execute('INSERT INTO BranchManager (BranchID, EmployeeID, AssignedDate) VALUES (?, ?, CURDATE())',
        [req.params.id, ManagerID]);
    }
    res.json({ message: 'Branch updated' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const [result] = await db.execute('DELETE FROM Branch WHERE BranchID = ?', [req.params.id]);
    if (result.affectedRows === 0) return res.status(404).json({ error: 'Branch not found' });
    res.json({ message: 'Branch deleted' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;

