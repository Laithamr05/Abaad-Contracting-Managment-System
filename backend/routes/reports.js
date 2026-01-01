const express = require('express');
const router = express.Router();
const db = require('../config/database');

// All complex SQL queries from queries.sql

router.get('/profitability', async (req, res) => {
  try {
    const query = `
      SELECT p.ProjectID, p.ProjectName, b.BranchName, c.ClientName, p.Revenue,
        COALESCE(material_costs.TotalMaterialCost, 0) AS MaterialCost,
        COALESCE(labor_costs.TotalLaborCost, 0) AS LaborCost,
        (p.Revenue - COALESCE(material_costs.TotalMaterialCost, 0) - COALESCE(labor_costs.TotalLaborCost, 0)) AS Profit,
        CASE WHEN p.Revenue > 0 THEN 
          ROUND(((p.Revenue - COALESCE(material_costs.TotalMaterialCost, 0) - COALESCE(labor_costs.TotalLaborCost, 0)) / p.Revenue) * 100, 2)
        ELSE 0 END AS ProfitMargin
      FROM Project p
      INNER JOIN Branch b ON p.BranchID = b.BranchID
      INNER JOIN Client c ON p.ClientID = c.ClientID
      LEFT JOIN (SELECT ProjectID, SUM(Quantity * UnitPrice) AS TotalMaterialCost FROM ProjectMaterial GROUP BY ProjectID) material_costs ON p.ProjectID = material_costs.ProjectID
      LEFT JOIN (SELECT wa.ProjectID, SUM(wa.HoursWorked * (e.Salary / 160)) AS TotalLaborCost FROM WorkAssignment wa INNER JOIN Employee e ON wa.EmployeeID = e.EmployeeID GROUP BY wa.ProjectID) labor_costs ON p.ProjectID = labor_costs.ProjectID
      ORDER BY Profit DESC
    `;
    const [rows] = await db.execute(query);
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/supplier-impact', async (req, res) => {
  try {
    const query = `
      WITH SupplierProjectMapping AS (
        SELECT DISTINCT sm.SupplierID, pm.ProjectID, SUM(pm.Quantity * pm.UnitPrice) AS ProjectValue
        FROM SupplierMaterial sm
        INNER JOIN ProjectMaterial pm ON sm.MaterialID = pm.MaterialID
        WHERE sm.Price <= pm.UnitPrice * 1.1
        GROUP BY sm.SupplierID, pm.ProjectID
      ),
      SupplierStats AS (
        SELECT s.SupplierID, s.SupplierName,
          COUNT(DISTINCT spm.ProjectID) AS ProjectCount,
          COALESCE(SUM(spm.ProjectValue), 0) AS TotalValue
        FROM Supplier s
        LEFT JOIN SupplierProjectMapping spm ON s.SupplierID = spm.SupplierID
        GROUP BY s.SupplierID, s.SupplierName
      )
      SELECT SupplierID, SupplierName, ProjectCount, TotalValue,
        DENSE_RANK() OVER (ORDER BY ProjectCount DESC, TotalValue DESC) AS RankByProjectCount,
        DENSE_RANK() OVER (ORDER BY TotalValue DESC, ProjectCount DESC) AS RankByValue
      FROM SupplierStats
      ORDER BY ProjectCount DESC, TotalValue DESC
    `;
    const [rows] = await db.execute(query);
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/hot-materials', async (req, res) => {
  try {
    const query = `
      WITH MaterialTotals AS (
        SELECT m.MaterialID, m.MaterialName, SUM(pm.Quantity * pm.UnitPrice) AS TotalCost,
          (SELECT SUM(Quantity * UnitPrice) FROM ProjectMaterial) AS GrandTotal
        FROM Material m
        INNER JOIN ProjectMaterial pm ON m.MaterialID = pm.MaterialID
        GROUP BY m.MaterialID, m.MaterialName
      ),
      TopProjectsPerMaterial AS (
        SELECT pm.MaterialID, pm.ProjectID, p.ProjectName,
          pm.Quantity * pm.UnitPrice AS ProjectCost,
          ROW_NUMBER() OVER (PARTITION BY pm.MaterialID ORDER BY pm.Quantity * pm.UnitPrice DESC) AS rn
        FROM ProjectMaterial pm
        INNER JOIN Project p ON pm.ProjectID = p.ProjectID
      )
      SELECT mt.MaterialID, mt.MaterialName, mt.TotalCost,
        ROUND((mt.TotalCost / mt.GrandTotal) * 100, 2) AS PercentageShare,
        MAX(CASE WHEN tpp.rn = 1 THEN CONCAT(tpp.ProjectName, ' (', FORMAT(tpp.ProjectCost, 2), ')') END) AS TopProject1,
        MAX(CASE WHEN tpp.rn = 2 THEN CONCAT(tpp.ProjectName, ' (', FORMAT(tpp.ProjectCost, 2), ')') END) AS TopProject2,
        MAX(CASE WHEN tpp.rn = 3 THEN CONCAT(tpp.ProjectName, ' (', FORMAT(tpp.ProjectCost, 2), ')') END) AS TopProject3
      FROM MaterialTotals mt
      LEFT JOIN TopProjectsPerMaterial tpp ON mt.MaterialID = tpp.MaterialID AND tpp.rn <= 3
      GROUP BY mt.MaterialID, mt.MaterialName, mt.TotalCost, mt.GrandTotal
      ORDER BY mt.TotalCost DESC
    `;
    const [rows] = await db.execute(query);
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/employee-utilization', async (req, res) => {
  try {
    const query = `
      WITH ManagementTree AS (
        SELECT e.ManagerID, e.EmployeeID, e.EmployeeName, e.RoleID, r.Title AS RoleTitle
        FROM Employee e
        INNER JOIN Role r ON e.RoleID = r.RoleID
        WHERE e.ManagerID IS NOT NULL
      ),
      ManagerSubordinateStats AS (
        SELECT mt.ManagerID, m.EmployeeName AS ManagerName,
          COUNT(DISTINCT mt.EmployeeID) AS SubordinateCount,
          SUM(COALESCE(wa.HoursWorked, 0)) AS TotalTeamHours,
          GROUP_CONCAT(DISTINCT mt.EmployeeName ORDER BY mt.EmployeeName SEPARATOR ', ') AS SubordinateNames
        FROM ManagementTree mt
        INNER JOIN Employee m ON mt.ManagerID = m.EmployeeID
        LEFT JOIN WorkAssignment wa ON mt.EmployeeID = wa.EmployeeID
        INNER JOIN Project p ON wa.ProjectID = p.ProjectID AND p.Status IN ('Active', 'Planning')
        GROUP BY mt.ManagerID, m.EmployeeName
      ),
      TopProjectsPerManager AS (
        SELECT mt.ManagerID, wa.ProjectID, p.ProjectName,
          SUM(wa.HoursWorked) AS TeamProjectHours,
          ROW_NUMBER() OVER (PARTITION BY mt.ManagerID ORDER BY SUM(wa.HoursWorked) DESC) AS rn
        FROM ManagementTree mt
        INNER JOIN WorkAssignment wa ON mt.EmployeeID = wa.EmployeeID
        INNER JOIN Project p ON wa.ProjectID = p.ProjectID AND p.Status IN ('Active', 'Planning')
        GROUP BY mt.ManagerID, wa.ProjectID, p.ProjectName
      )
      SELECT mss.ManagerID, mss.ManagerName, mss.SubordinateCount,
        ROUND(mss.TotalTeamHours, 2) AS TotalTeamHours,
        tpp.ProjectName AS TopProjectByHours,
        ROUND(tpp.TeamProjectHours, 2) AS TopProjectHours,
        mss.SubordinateNames
      FROM ManagerSubordinateStats mss
      LEFT JOIN TopProjectsPerManager tpp ON mss.ManagerID = tpp.ManagerID AND tpp.rn = 1
      ORDER BY mss.SubordinateCount DESC, mss.TotalTeamHours DESC
    `;
    const [rows] = await db.execute(query);
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/price-anomalies', async (req, res) => {
  try {
    const query = `
      WITH SupplierMinPrices AS (
        SELECT MaterialID, MIN(Price) AS MinSupplierPrice,
          AVG(Price) AS AvgSupplierPrice, MAX(Price) AS MaxSupplierPrice
        FROM SupplierMaterial GROUP BY MaterialID
      ),
      AnomalyAnalysis AS (
        SELECT pm.ProjectID, p.ProjectName, m.MaterialID, m.MaterialName,
          m.BaseUnitPrice AS BaseUnitPrice, COALESCE(smp.MinSupplierPrice, 0) AS MinSupplierPrice,
          COALESCE(smp.AvgSupplierPrice, 0) AS AvgSupplierPrice, pm.UnitPrice AS ProjectUnitPrice, pm.Quantity,
          CASE WHEN COALESCE(smp.MinSupplierPrice, 0) > 0 THEN 
            ((pm.UnitPrice - smp.MinSupplierPrice) / smp.MinSupplierPrice) * 100
          ELSE NULL END AS PriceVariancePercent,
          (pm.UnitPrice - m.BaseUnitPrice) AS DeviationFromBase,
          CASE 
            WHEN COALESCE(smp.MinSupplierPrice, 0) > 0 AND pm.UnitPrice > smp.MinSupplierPrice * 1.2 THEN 'HIGH'
            WHEN COALESCE(smp.MinSupplierPrice, 0) > 0 AND pm.UnitPrice > smp.MinSupplierPrice * 1.1 THEN 'MEDIUM'
            ELSE 'LOW'
          END AS AnomalyLevel
        FROM ProjectMaterial pm
        INNER JOIN Material m ON pm.MaterialID = m.MaterialID
        INNER JOIN Project p ON pm.ProjectID = p.ProjectID
        LEFT JOIN SupplierMinPrices smp ON m.MaterialID = smp.MaterialID
      )
      SELECT ProjectID, ProjectName, MaterialID, MaterialName,
        BaseUnitPrice, MinSupplierPrice, AvgSupplierPrice, ProjectUnitPrice, Quantity,
        ROUND(PriceVariancePercent, 2) AS PriceVariancePercent,
        ROUND(DeviationFromBase, 2) AS DeviationFromBase, AnomalyLevel,
        (ProjectUnitPrice * Quantity) AS TotalCostImpact
      FROM AnomalyAnalysis
      WHERE AnomalyLevel IN ('HIGH', 'MEDIUM')
      ORDER BY PriceVariancePercent DESC, TotalCostImpact DESC
    `;
    const [rows] = await db.execute(query);
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/branch-performance', async (req, res) => {
  try {
    const query = `
      WITH BranchProjectStats AS (
        SELECT b.BranchID, b.BranchName, b.City,
          COUNT(DISTINCT e.EmployeeID) AS EmployeeCount,
          COUNT(DISTINCT p.ProjectID) AS ProjectCount,
          SUM(p.Revenue) AS TotalRevenue,
          COUNT(DISTINCT CASE WHEN p.Status = 'Active' THEN p.ProjectID END) AS ActiveProjects,
          COUNT(DISTINCT CASE WHEN p.Status = 'Completed' THEN p.ProjectID END) AS CompletedProjects
        FROM Branch b
        LEFT JOIN Employee e ON b.BranchID = e.BranchID
        LEFT JOIN Project p ON b.BranchID = p.BranchID
        GROUP BY b.BranchID, b.BranchName, b.City
      ),
      BranchCostStats AS (
        SELECT p.BranchID,
          COALESCE(SUM(pm.Quantity * pm.UnitPrice), 0) AS TotalMaterialCost,
          COALESCE(SUM(wa.HoursWorked * (e.Salary / 160)), 0) AS TotalLaborCost
        FROM Project p
        LEFT JOIN ProjectMaterial pm ON p.ProjectID = pm.ProjectID
        LEFT JOIN WorkAssignment wa ON p.ProjectID = wa.ProjectID
        LEFT JOIN Employee e ON wa.EmployeeID = e.EmployeeID
        GROUP BY p.BranchID
      )
      SELECT bps.BranchID, bps.BranchName, bps.City, bps.EmployeeCount,
        bps.ProjectCount, bps.ActiveProjects, bps.CompletedProjects,
        bps.TotalRevenue, COALESCE(bcs.TotalMaterialCost, 0) AS TotalMaterialCost,
        COALESCE(bcs.TotalLaborCost, 0) AS TotalLaborCost,
        (COALESCE(bcs.TotalMaterialCost, 0) + COALESCE(bcs.TotalLaborCost, 0)) AS TotalCost,
        (bps.TotalRevenue - COALESCE(bcs.TotalMaterialCost, 0) - COALESCE(bcs.TotalLaborCost, 0)) AS NetProfit,
        CASE WHEN bps.TotalRevenue > 0 THEN 
          ROUND(((bps.TotalRevenue - COALESCE(bcs.TotalMaterialCost, 0) - COALESCE(bcs.TotalLaborCost, 0)) / bps.TotalRevenue) * 100, 2)
        ELSE 0 END AS ProfitMargin,
        e.EmployeeName AS BranchManagerName
      FROM BranchProjectStats bps
      LEFT JOIN BranchCostStats bcs ON bps.BranchID = bcs.BranchID
      LEFT JOIN BranchManager bm ON bps.BranchID = bm.BranchID
      LEFT JOIN Employee e ON bm.EmployeeID = e.EmployeeID
      ORDER BY NetProfit DESC
    `;
    const [rows] = await db.execute(query);
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;

