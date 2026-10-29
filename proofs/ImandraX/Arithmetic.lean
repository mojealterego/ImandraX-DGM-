/-!
  ImandraX Ω: small, independently kernel-checkable arithmetic foundation.
  These lemmas formalize a tiny subset of mathematics, not all MSC2020.
  All declarations below are checked by the Lean kernel.
-/
namespace ImandraX

theorem nat_add_left_identity (n : Nat) : 0 + n = n := Nat.zero_add n
theorem nat_add_right_identity (n : Nat) : n + 0 = n := Nat.add_zero n
theorem nat_add_commutative (a b : Nat) : a + b = b + a := Nat.add_comm a b
theorem nat_add_associative (a b c : Nat) : (a + b) + c = a + (b + c) :=
  Nat.add_assoc a b c

theorem nat_mul_left_identity (n : Nat) : 1 * n = n := Nat.one_mul n
theorem nat_mul_right_identity (n : Nat) : n * 1 = n := Nat.mul_one n
theorem nat_mul_commutative (a b : Nat) : a * b = b * a := Nat.mul_comm a b

theorem equality_transitive {α : Sort u} {a b c : α} (h₁ : a = b) (h₂ : b = c) : a = c :=
  Eq.trans h₁ h₂

theorem conjunction_associative (p q r : Prop) : (p ∧ q) ∧ r ↔ p ∧ (q ∧ r) := by
  constructor
  · intro h
    exact ⟨h.left.left, h.left.right, h.right⟩
  · intro h
    exact ⟨⟨h.left, h.right.left⟩, h.right.right⟩

end ImandraX
