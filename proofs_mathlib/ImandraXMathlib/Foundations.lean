/-!
ImandraX × DGM × RSI Ω: genuinely formalized, narrowly scoped examples.
The statements below are proved in Lean. Their MSC tags are research metadata,
not an assertion that an entire MSC category is formalized.
-/
import Mathlib

namespace ImandraXMathlib

/-- Elementary polynomial identity over the integers. -/
theorem polynomial_square (x y : ℤ) :
    (x + y) ^ 2 = x ^ 2 + 2 * x * y + y ^ 2 := by
  ring

/-- Elementary multiplicative number theory. -/
theorem nat_divides_product (a b : ℕ) : a ∣ a * b := by
  exact ⟨b, rfl⟩

/-- Triangle inequality in the reals. -/
theorem abs_triangle (x y : ℝ) : |x + y| ≤ |x| + |y| :=
  abs_add_le x y

/-- Monotonicity of integer addition. -/
theorem int_add_monotone (a b c : ℤ) (h : a ≤ b) : a + c ≤ b + c := by
  omega

/-- Conjunction is commutative. -/
theorem conjunction_commutes (p q : Prop) : p ∧ q ↔ q ∧ p := by
  constructor
  · intro h
    exact ⟨h.2, h.1⟩
  · intro h
    exact ⟨h.2, h.1⟩

/-- Intersection is included in its left operand. -/
theorem intersection_subset_left {α : Type*} (A B : Set α) : A ∩ B ⊆ A := by
  intro x hx
  exact hx.1

/-- Union is commutative. -/
theorem union_commutes {α : Type*} (A B : Set α) : A ∪ B = B ∪ A := by
  ext x
  simp [or_comm]

/-- Natural number exponentiation respects additive exponents. -/
theorem natural_power_add (x m n : ℕ) : x ^ (m + n) = x ^ m * x ^ n := by
  exact pow_add x m n

/-- Function composition is associative. -/
theorem composition_associative {α β γ δ : Type*}
    (f : γ → δ) (g : β → γ) (h : α → β) :
    (f ∘ g) ∘ h = f ∘ (g ∘ h) := by
  rfl

end ImandraXMathlib
