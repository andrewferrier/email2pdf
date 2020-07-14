class Email2pdf < Formula
  desc "Email2PDF"
  homepage "http://github.com/andrewferrier/email2pdf"
  url "https://github.com/andrewferrier/email2pdf/archive/X.Y.zip"
  version "X.Y"

  depends_on "python@3"
  depends_on "libmagic"

  def install
      bin.install "email2pdf"
      doc.install "README.md", "LICENSE.txt"
  end
end
