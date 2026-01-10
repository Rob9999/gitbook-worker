---
title: Chapter 1 – Observable patterns
date: 2024-06-01
version: 1.0
doc_type: chapter
chapter_number: 1
---

# Chapter 1 – Observable patterns

In software development, we repeatedly encounter similar problems for which proven solutions have been established over time. These recurring structures are referred to as design patterns.

## Historical development

The systematic documentation of design patterns began in the 1990s. Inspired by architecture, where Christopher Alexander described patterns for building construction, software developers transferred this idea to programming.

### Early pioneers

The so-called "Gang of Four" (Gamma, Helm, Johnson, Vlissides) published the seminal work "Design Patterns" in 1994, which categorised and described 23 patterns.

### Modern developments

Today, hundreds of documented patterns exist for a wide variety of application areas – from microservices and reactive programming to cloud architectures.

## Categories of patterns

Design patterns can be divided into three main categories:

### Creational patterns

These patterns deal with object creation and attempt to make object instantiation more flexible:

- **Singleton**: Ensures that only one instance of a class exists
- **Factory**: Encapsulates object creation
- **Builder**: Separates the construction of complex objects from their representation

### Structural patterns

Structural patterns describe how classes and objects can be composed into larger structures:

- **Adapter**: Enables collaboration between incompatible interfaces
- **Composite**: Forms tree structures to represent part-whole hierarchies
- **Decorator**: Dynamically extends objects with additional functionality

### Behavioural patterns

These patterns address the interaction between objects and the distribution of responsibilities:

- **Observer**: Defines a dependency between objects so that changes are automatically propagated
- **Strategy**: Encapsulates interchangeable algorithms
- **Command**: Encapsulates requests as objects

## Advantages of using patterns

Using established design patterns offers several advantages:

1. **Common language**: Teams can communicate complex concepts precisely
2. **Proven solutions**: Patterns have been proven in practice and are well documented
3. **Maintainability**: Code becomes more structured and easier to understand
4. **Flexibility**: Changes can often be implemented with less effort

## Limitations and challenges

Despite their advantages, design patterns are not a panacea:

- **Over-engineering**: Not every problem requires a complex pattern
- **Learning curve**: Understanding and correct application require experience
- **Context dependency**: A pattern must fit the specific situation

## Practical application

When deciding on a design pattern, the following questions should be asked:

1. What problem needs to be solved?
2. Is there an established pattern for this problem?
3. Does the complexity of the pattern justify the expected benefit?
4. Does the pattern fit with the existing architecture?

## Summary

Design patterns are a valuable tool in software development. They provide tested solutions for recurring problems and promote a common technical language. However, their sensible application requires experience and judgement to avoid falling into the trap of over-engineering.
