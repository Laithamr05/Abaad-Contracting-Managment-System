const express = require('express');
const router = express.Router();
const db = require('../config/database');

router.get('/', async (req, res) => {
  try {
    const [rows] = await db.execute(`
      SELECT p.*, b.BranchName, c.ClientName
      FROM Project p
      LEFT JOIN Branch b ON p.BranchID = b.BranchID
      LEFT JOIN Client c ON p.ClientID = c.ClientID
      ORDER BY p.ProjectName
    `);
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/:id', async (req, res) => {
  try {
    const [rows] = await db.execute(`
      SELECT p.*, b.BranchName, c.ClientName
      FROM Project p
      LEFT JOIN Branch b ON p.BranchID = b.BranchID
      LEFT JOIN Client c ON p.ClientID = c.ClientID
      WHERE p.ProjectID = ?
    `, [req.params.id]);
    if (rows.length === 0) return res.status(404).json({ error: 'Project not found' });
    res.json(rows[0]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/', async (req, res) => {
  try {
    const { ProjectName, Location, Cost, Revenue, BranchID, ClientID, StartDate, EndDate, Status } = req.body;
    if (!ProjectName || !BranchID || !ClientID || !StartDate) {
      return res.status(400).json({ error: 'ProjectName, BranchID, ClientID, StartDate required' });
    }
    const [result] = await db.execute(
      `INSERT INTO Project (ProjectName, Location, Cost, Revenue, BranchID, ClientID, StartDate, EndDate, Status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [ProjectName, Location || null, Cost || 0, Revenue || 0, BranchID, ClientID, StartDate, EndDate || null, Status || 'Planning']
    );
    res.status(201).json({ ProjectID: result.insertId, message: 'Project created' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.put('/:id', async (req, res) => {
  try {
    const { ProjectName, Location, Cost, Revenue, BranchID, ClientID, StartDate, EndDate, Status } = req.body;
    await db.execute(
      `UPDATE Project SET ProjectName = ?, Location = ?, Cost = ?, Revenue = ?, BranchID = ?, 
       ClientID = ?, StartDate = ?, EndDate = ?, Status = ? WHERE ProjectID = ?`,
      [ProjectName, Location || null, Cost || 0, Revenue || 0, BranchID, ClientID, StartDate, EndDate || null, Status || 'Planning', req.params.id]
    );
    res.json({ message: 'Project updated' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.delete('/:id', async (req, res) => {
  try {
    const [result] = await db.execute('DELETE FROM Project WHERE ProjectID = ?', [req.params.id]);
    if (result.affectedRows === 0) return res.status(404).json({ error: 'Project not found' });
    res.json({ message: 'Project deleted' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;

