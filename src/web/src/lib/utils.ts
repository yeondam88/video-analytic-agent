import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Combines multiple class names into a single string, filtering out falsy values.
 * This is useful for conditional class names in React components.
 * 
 * @param classes - Array of class names or conditional expressions that resolve to class names
 * @returns A string of combined class names
 */
export function classNames(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
} 