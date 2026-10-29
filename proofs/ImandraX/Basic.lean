namespace ImandraX

theorem add_zero (n : Nat) : n + 0 = n := Nat.add_zero n

theorem identity_implication (p : Prop) : p → p := by
  intro hp
  exact hp

theorem and_commute (p q : Prop) : p ∧ q → q ∧ p := by
  intro hpq
  exact And.intro hpq.right hpq.left

end ImandraX