SELECT s.ID,
       s.Name,
       s.Capacity,
       COUNT(p.ID) AS TotalPets,
       SUM(CASE WHEN p.AdoptionStatus != 'Adopted' THEN 1 ELSE 0 END) AS CurrentlyHoused
FROM Shelter s
LEFT JOIN Pet p ON p.Shelter_ID = s.ID
GROUP BY s.ID
ORDER BY s.ID;